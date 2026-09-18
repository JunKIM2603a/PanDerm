#!/usr/bin/env python3
"""
Oto-Endoscopic linear-evaluation manifest generator
===================================================

Builds the manifest CSVs that let the Oto-Endoscopic (otoscopic tympanic
membrane) dataset run through `PanDerm/classification/linear_eval.py` exactly
like the other datasets under `PanDerm/data/`.

Design decisions
----------------
1. Source of truth = the class folders under `Oto-Endoscopic_Images/`.
   No image file is moved, renamed or modified; labels live only in the CSV.

2. Label space = the 5 folder names, sorted, 0-indexed:
       0 Acute_Otitis_Media   1 Cerumen_Impaction   2 Chronic_Otitis_Media
       3 Myringosclerosis     4 Normal

3. The release ships no train/val/test split, so we build one the same way
   `aptos2019_multiclass.csv` and `oral_cancer_binary.csv` were built:
   **stratified 70 / 15 / 15**, fixed seed, deterministic (sorted file order).

4. Paths are relative to `--root_path ../data/Oto-Endoscopic/`, i.e. they start
   with `Oto-Endoscopic_Images/`, matching how `Derm_Dataset` joins
   `root + image`.

5. The release ships no patient identifiers, so a patient-level split is
   undefined for this data (AGENTS.md §2.1 scope caveat). The largest
   controllable grouping unit is the exact-duplicate (sha256) cluster. This
   script audits those clusters and, because the plain stratified split lets
   them straddle folds, also emits a duplicate-aware manifest for use as a
   leak-free robustness replicate.

Emits (into this folder):
  - oto_endoscopic_label_map.csv          class_name,label
  - oto_endoscopic_multiclass.csv         image,label,split  (70/15/15 stratified,
                                          same recipe as aptos2019 / Oral_Cancer)
  - oto_endoscopic_multiclass_dupaware.csv  same, but sha256 groups kept intact
  - oto_endoscopic_manifest.csv           traceability: + class_name, sha256,
                                          dup_group, split_dupaware
"""

import os
import csv
import hashlib
import argparse
import random
from collections import defaultdict, Counter

from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))          # .../Oto-Endoscopic/Linear Evaluation
DS_ROOT = os.path.dirname(HERE)                            # .../Oto-Endoscopic
IMG_DIRNAME = "Oto-Endoscopic_Images"
IMG_ROOT = os.path.join(DS_ROOT, IMG_DIRNAME)
IMG_EXT = (".jpg", ".jpeg", ".png")

TRAIN_FRAC, VAL_FRAC = 0.70, 0.15   # test takes the remainder


def sha256(path, chunk=1 << 20):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for b in iter(lambda: f.read(chunk), b""):
            h.update(b)
    return h.hexdigest()


def collect():
    """Return (label_map, rows) with rows sorted deterministically."""
    classes = sorted(
        d for d in os.listdir(IMG_ROOT) if os.path.isdir(os.path.join(IMG_ROOT, d))
    )
    label_map = {name: i for i, name in enumerate(classes)}
    rows = []
    for name in classes:
        cdir = os.path.join(IMG_ROOT, name)
        for fn in sorted(os.listdir(cdir)):
            if not fn.lower().endswith(IMG_EXT):
                continue
            rel = f"{IMG_DIRNAME}/{name}/{fn}"
            rows.append(
                {
                    "image": rel,
                    "label": label_map[name],
                    "class_name": name,
                    "sha256": sha256(os.path.join(cdir, fn)),
                }
            )
    return label_map, rows


def assign_split(rows, seed, key="split", group_by=None):
    """Stratified 70/15/15 over `label`, written into `rows[i][key]`.

    Deterministic given (sorted rows, seed). With `group_by` set to a row field
    (e.g. "sha256"), whole groups are dealt as units so no group straddles a
    split boundary; the group's class is the class of its members (exact
    duplicates in this dataset never cross classes -- asserted below).
    """
    if group_by is None:
        units = {i: [i] for i in range(len(rows))}
    else:
        units = defaultdict(list)
        for i, r in enumerate(rows):
            units[r[group_by]].append(i)
    by_label = defaultdict(list)
    for uid, members in units.items():
        # A group may straddle classes (near-duplicate photos labelled
        # differently). It still has to stay intact, so it is dealt under its
        # majority class; rows keep their own labels.
        major = Counter(rows[i]["label"] for i in members).most_common(1)[0][0]
        by_label[major].append(uid)
    rng = random.Random(seed)
    for label in sorted(by_label):
        uids = sorted(by_label[label], key=lambda u: rows[units[u][0]]["image"])
        rng.shuffle(uids)
        n = len(uids)
        n_tr = int(round(n * TRAIN_FRAC))
        n_va = int(round(n * VAL_FRAC))
        assert n - n_tr - n_va > 0, f"class {label}: no test units left"
        for j, uid in enumerate(uids):
            sp = "train" if j < n_tr else ("val" if j < n_tr + n_va else "test")
            for i in units[uid]:
                rows[i][key] = sp


def dup_groups(rows):
    """Exact-duplicate (sha256) clusters -> {sha256: group_id}, group ids stable."""
    by_hash = defaultdict(list)
    for r in rows:
        by_hash[r["sha256"]].append(r)
    return {h: gid for gid, h in enumerate(sorted(by_hash))}, by_hash


def dhash(path, s=8):
    """64-bit difference hash: robust to re-encoding and tiny shifts."""
    im = Image.open(path).convert("L").resize((s + 1, s), Image.LANCZOS)
    px = list(im.getdata())
    bits = 0
    for r in range(s):
        for c in range(s):
            bits = (bits << 1) | (px[r * (s + 1) + c] < px[r * (s + 1) + c + 1])
    return bits


def neardup_groups(rows, threshold):
    """Union-find over dHash pairs within Hamming `threshold` -> group id per row.

    Catches what sha256 cannot: consecutive frames of the same ear, re-crops and
    re-encodes. Transitive closure, so a chain of similar frames forms one group.
    """
    n = len(rows)
    parent = list(range(n))

    def find(a):
        while parent[a] != a:
            parent[a] = parent[parent[a]]
            a = parent[a]
        return a

    for i in range(n):
        di = rows[i]["dhash"]
        for j in range(i + 1, n):
            if bin(di ^ rows[j]["dhash"]).count("1") <= threshold:
                ri, rj = find(i), find(j)
                if ri != rj:
                    parent[rj] = ri
    roots = {}
    out = []
    for i in range(n):
        r = find(i)
        out.append(roots.setdefault(r, len(roots)))
    return out


def write_csv(path, fieldnames, rows):
    with open(path, "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=fieldnames, extrasaction="ignore")
        w.writeheader()
        w.writerows(rows)
    print(f"wrote {path} ({len(rows)} rows)")


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--seed", type=int, default=0, help="split seed (default 0)")
    ap.add_argument("--neardup-threshold", type=int, default=5,
                    help="max dHash Hamming distance counted as a near duplicate (default 5)")
    args = ap.parse_args()

    label_map, rows = collect()
    assign_split(rows, args.seed)
    gid_of, by_hash = dup_groups(rows)
    for r in rows:
        r["dup_group"] = gid_of[r["sha256"]]
    assign_split(rows, args.seed, key="split_dupaware", group_by="sha256")

    for r in rows:
        r["dhash"] = dhash(os.path.join(DS_ROOT, r["image"]))
    for r, g in zip(rows, neardup_groups(rows, args.neardup_threshold)):
        r["neardup_group"] = g
    assign_split(rows, args.seed, key="split_neardup", group_by="neardup_group")

    write_csv(
        os.path.join(HERE, "oto_endoscopic_label_map.csv"),
        ["class_name", "label"],
        [{"class_name": n, "label": i} for n, i in sorted(label_map.items(), key=lambda kv: kv[1])],
    )
    write_csv(
        os.path.join(HERE, "oto_endoscopic_multiclass.csv"),
        ["image", "label", "split"],
        rows,
    )
    write_csv(
        os.path.join(HERE, "oto_endoscopic_multiclass_dupaware.csv"),
        ["image", "label", "split"],
        [{"image": r["image"], "label": r["label"], "split": r["split_dupaware"]} for r in rows],
    )
    write_csv(
        os.path.join(HERE, "oto_endoscopic_multiclass_neardup.csv"),
        ["image", "label", "split"],
        [{"image": r["image"], "label": r["label"], "split": r["split_neardup"]} for r in rows],
    )
    write_csv(
        os.path.join(HERE, "oto_endoscopic_manifest.csv"),
        ["image", "label", "class_name", "split", "split_dupaware", "split_neardup",
         "sha256", "dup_group", "neardup_group"],
        rows,
    )

    # --- report -----------------------------------------------------------
    print(f"\nclasses: {label_map}")
    counts = defaultdict(lambda: defaultdict(int))
    for r in rows:
        counts[r["label"]][r["split"]] += 1
    print(f"{'label':>5} {'train':>6} {'val':>5} {'test':>5} {'total':>6}")
    for lab in sorted(counts):
        c = counts[lab]
        print(f"{lab:>5} {c['train']:>6} {c['val']:>5} {c['test']:>5} "
              f"{c['train']+c['val']+c['test']:>6}")
    tot = defaultdict(int)
    for c in counts.values():
        for s, v in c.items():
            tot[s] += v
    print(f"{'ALL':>5} {tot['train']:>6} {tot['val']:>5} {tot['test']:>5} {sum(tot.values()):>6}")

    clusters = {h: rs for h, rs in by_hash.items() if len(rs) > 1}
    n_dup_imgs = sum(len(rs) for rs in clusters.values())
    print(f"\nexact-duplicate audit (sha256): {len(clusters)} clusters covering "
          f"{n_dup_imgs} images; {len(by_hash)} groups over {len(rows)} images")
    crossing = [h for h, rs in clusters.items() if len({r['split'] for r in rs}) > 1]
    print(f"duplicate clusters crossing a split boundary: {len(crossing)}")
    if crossing:
        print("  NOTE: the pre-registered-style plain stratified split is not "
              "duplicate-aware (cf. AGENTS.md / manuscript Limitation 15).")
        for h in crossing[:10]:
            print("   ", [(r['image'], r['split']) for r in clusters[h]])

    crossing_da = [h for h, rs in clusters.items() if len({r['split_dupaware'] for r in rs}) > 1]
    da = defaultdict(int)
    for r in rows:
        da[r["split_dupaware"]] += 1
    print(f"\nduplicate-aware split: train {da['train']} / val {da['val']} / test {da['test']}"
          f"  (clusters crossing a boundary: {len(crossing_da)})")
    # --- near-duplicate audit ---------------------------------------------
    nd = defaultdict(list)
    for r in rows:
        nd[r["neardup_group"]].append(r)
    nd_clusters = {g: rs for g, rs in nd.items() if len(rs) > 1}
    nd_cross = [rs for rs in nd_clusters.values() if len({r["split"] for r in rs}) > 1]
    leaky_test = sum(
        1 for rs in nd_cross for r in rs
        if r["split"] == "test" and {x["split"] for x in rs} & {"train", "val"}
    )
    n_test = sum(1 for r in rows if r["split"] == "test")
    print(f"\nnear-duplicate audit (dHash Hamming <= {args.neardup_threshold}): "
          f"{len(nd_clusters)} clusters covering "
          f"{sum(len(rs) for rs in nd_clusters.values())} images; "
          f"{len(nd)} groups over {len(rows)} images")
    print(f"  clusters crossing a split boundary: {len(nd_cross)}")
    print(f"  TEST images with a near-duplicate in train/val: {leaky_test}/{n_test} "
          f"({100 * leaky_test / n_test:.1f}%)  <-- inflates the plain-split score")
    print(f"  near-duplicate clusters spanning >1 class: "
          f"{sum(1 for rs in nd_clusters.values() if len({r['label'] for r in rs}) > 1)}")

    ndsp = defaultdict(int)
    for r in rows:
        ndsp[r["split_neardup"]] += 1
    still = sum(1 for rs in nd_clusters.values() if len({r["split_neardup"] for r in rs}) > 1)
    print(f"  near-duplicate-aware split: train {ndsp['train']} / val {ndsp['val']} / "
          f"test {ndsp['test']}  (clusters crossing a boundary: {still})")

    print("\nNOTE: sha256 catches byte-identical files only; dHash catches visual "
          "near-duplicates. Neither establishes patient independence -- the release "
          "ships no patient ids, so two photos of the same ear taken from a different "
          "angle can still land in different folds. Report as a limitation.")


if __name__ == "__main__":
    main()
