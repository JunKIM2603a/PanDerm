#!/usr/bin/env python3
"""
SMART-OM label remapping generator
==================================

Builds the label-remapping artifacts that let SMART-OM (Figshare) serve as an
external validation set for a PanDerm linear probe trained on Oral_Diseases (MOD).

Design decisions (see README_remapping.md for the full rationale):

1. Canonical image set = "01. Unannotated" ONLY.
   SMART-OM stores every photo four times (Unannotated / Region / Full / Lesion).
   Region/Full/Lesion have annotation polygons *baked into the pixels* (verified:
   same filename + same dimensions but different bytes, yellow polygon overlays),
   so they would corrupt PanDerm features. Only "01. Unannotated" is the clean
   raw photo. This also matches the paper's reported 2,469-image count.

2. Target label space = coarse 3-level malignancy risk, shared with MOD:
       0 = benign_normal   (양성/정상)
       1 = OPMD            (구강잠재악성질환)
       2 = oral_cancer     (구강암)
   This is the only axis on which MOD and SMART-OM harmonise cleanly (§2-4 of the
   10th-meeting minutes). No re-labeling of image files on disk — labels live only
   in the emitted CSVs (respects the CC BY-NC-ND license).

3. SMART-OM 4 -> 3 mapping:
       01. Normal              -> 0 benign_normal
       02. Variation from normal -> 0 benign_normal
       03. OPMD                -> 1 OPMD
       04. Oral Cancer         -> 2 oral_cancer

4. MOD 7 -> 3 mapping (for the paired probe-training source):
       CaS, CoS, Gum, OT       -> 0 benign_normal   (benign inflammatory/infectious)
       OLP                     -> 1 OPMD            (WHO 2020 classifies OLP as OPMD)
       MC, OC                  -> 2 oral_cancer

Emits (into this folder):
  - smart_om_3class_label_map.csv          the 3-class label map
  - smart_om_remapping_3class.csv          SMART-OM only, split=test, paths rel. to SMART-OM_remapping/
  - smart_om_remapping_manifest.csv        full traceability (patient, region, original class)
  - mod_smartom_external_val_3class.csv    MOD(train) + SMART-OM(test), paths rel. to PanDerm/data/
"""

import os
import re
import csv
import glob
import argparse

# ---------------------------------------------------------------------------
# Paths
# ---------------------------------------------------------------------------
HERE = os.path.dirname(os.path.abspath(__file__))                 # .../SMART-OM_remapping/Linear Evaluation
SMARTOM_ROOT = os.path.dirname(HERE)                              # .../SMART-OM_remapping
DATA_ROOT = os.path.dirname(SMARTOM_ROOT)                         # .../PanDerm/data
SMARTOM_DIRNAME = os.path.basename(SMARTOM_ROOT)                  # "SMART-OM_remapping"
MOD_CSV = os.path.join(DATA_ROOT, "Oral_Diseases", "Linear Evaluation", "oral_diseases_multiclass.csv")
MOD_LABEL_MAP = os.path.join(DATA_ROOT, "Oral_Diseases", "Linear Evaluation", "oral_diseases_label_map.csv")

IMG_EXT = (".jpg", ".jpeg", ".png")
UNANNOTATED = "01. Unannotated"

# ---------------------------------------------------------------------------
# Mappings
# ---------------------------------------------------------------------------
# 3-class target space
LABEL_MAP_3 = [("benign_normal", 0), ("OPMD", 1), ("oral_cancer", 2)]
NAME_OF = {i: n for n, i in LABEL_MAP_3}

# SMART-OM top folder -> 3-class label
SMARTOM_CLASS_DIRS = {
    "01. Normal": 0,
    "02. Variation from normal": 0,
    "03. OPMD": 1,
    "04. Oral Cancer": 2,
}

# MOD class_name -> 3-class label
MOD_TO_3 = {
    "CaS": 0, "CoS": 0, "Gum": 0, "OT": 0,   # benign
    "OLP": 1,                                 # OPMD
    "MC": 2, "OC": 2,                         # cancer
}


def patient_id_from_name(basename: str):
    """Extract SMITA patient id if present (e.g. SMITA00187_W_LL.jpeg -> SMITA00187)."""
    m = re.match(r"(SMITA\d+)", basename)
    return m.group(1) if m else ""


def collect_smartom_rows():
    """Scan SMART-OM_remapping/*/01. Unannotated recursively; return manifest rows."""
    rows = []
    for cls_dir, label in SMARTOM_CLASS_DIRS.items():
        base = os.path.join(SMARTOM_ROOT, cls_dir, UNANNOTATED)
        if not os.path.isdir(base):
            continue
        for path in sorted(glob.glob(os.path.join(base, "**", "*"), recursive=True)):
            if not os.path.isfile(path):
                continue
            if not path.lower().endswith(IMG_EXT):
                continue
            rel_to_smartom = os.path.relpath(path, SMARTOM_ROOT)          # for standalone CSV
            rel_to_data = os.path.relpath(path, DATA_ROOT)               # for combined CSV
            region = os.path.basename(os.path.dirname(path))            # e.g. "06. Lower lip"
            basename = os.path.basename(path)
            rows.append({
                "image_rel_smartom": rel_to_smartom,
                "image_rel_data": rel_to_data,
                "label": label,
                "class_name_3": NAME_OF[label],
                "smartom_class_4": cls_dir,
                "region": region,
                "patient_id": patient_id_from_name(basename),
                "split": "test",
            })
    return rows


def load_mod_rows():
    """Load MOD multiclass CSV and remap 7-class labels to the 3-class space."""
    with open(MOD_LABEL_MAP, newline="") as f:
        id_to_name = {int(r["label"]): r["class_name"] for r in csv.DictReader(f)}
    rows = []
    with open(MOD_CSV, newline="") as f:
        for r in csv.DictReader(f):
            name7 = id_to_name[int(r["label"])]
            label3 = MOD_TO_3[name7]
            rows.append({
                "image_rel_data": os.path.join("Oral_Diseases", r["image"]),
                "label": label3,
                "orig_split": r["split"],
                "mod_class": name7,
            })
    return rows


def write_csv(path, header, rows):
    with open(path, "w", newline="") as f:
        w = csv.writer(f)
        w.writerow(header)
        w.writerows(rows)
    print(f"  wrote {path}  ({len(rows)} rows)")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--fold-mod-test-into-train", action="store_true", default=True,
                    help="Put MOD test fold into the probe TRAIN split (default: on, since "
                         "SMART-OM is the sole external test).")
    args = ap.parse_args()

    print("Scanning SMART-OM (Unannotated only) ...")
    som = collect_smartom_rows()
    print("Loading + remapping MOD ...")
    mod = load_mod_rows()

    # ---- label map ----
    write_csv(os.path.join(HERE, "smart_om_3class_label_map.csv"),
              ["class_name", "label"], [[n, i] for n, i in LABEL_MAP_3])

    # ---- SMART-OM standalone (paths relative to SMART-OM_remapping/) ----
    write_csv(os.path.join(HERE, "smart_om_remapping_3class.csv"),
              ["image", "label", "split"],
              [[r["image_rel_smartom"], r["label"], r["split"]] for r in som])

    # ---- full manifest (traceability) ----
    write_csv(os.path.join(HERE, "smart_om_remapping_manifest.csv"),
              ["image", "label", "class_name", "smartom_class_4", "region", "patient_id", "split"],
              [[r["image_rel_smartom"], r["label"], r["class_name_3"], r["smartom_class_4"],
                r["region"], r["patient_id"], r["split"]] for r in som])

    # ---- combined external-validation CSV (paths relative to PanDerm/data/) ----
    combined = []
    for r in mod:
        split = r["orig_split"]
        if split == "test" and args.fold_mod_test_into_train:
            split = "train"        # SMART-OM is the sole external test; use all MOD to fit
        combined.append([r["image_rel_data"], r["label"], split])
    for r in som:
        combined.append([r["image_rel_data"], r["label"], "test"])   # SMART-OM = external test
    write_csv(os.path.join(HERE, "mod_smartom_external_val_3class.csv"),
              ["image", "label", "split"], combined)

    # ---- report distributions ----
    def dist(rows, key):
        d = {}
        for r in rows:
            d[r[key]] = d.get(r[key], 0) + 1
        return dict(sorted(d.items()))

    print("\n=== SMART-OM 3-class distribution (test) ===")
    dsom = {}
    for r in som:
        dsom[r["class_name_3"]] = dsom.get(r["class_name_3"], 0) + 1
    total = sum(dsom.values())
    for name, _ in LABEL_MAP_3:
        n = dsom.get(name, 0)
        print(f"  {name:14s}: {n:5d}  ({100*n/total:5.2f}%)")
    print(f"  {'TOTAL':14s}: {total:5d}")
    n_patients = len({r["patient_id"] for r in som if r["patient_id"]})
    print(f"  distinct patients: {n_patients}")

    print("\n=== Combined external-val CSV split sizes ===")
    sd = {}
    for row in combined:
        sd[row[2]] = sd.get(row[2], 0) + 1
    print(" ", sd)
    print("\nDone.")


if __name__ == "__main__":
    main()
