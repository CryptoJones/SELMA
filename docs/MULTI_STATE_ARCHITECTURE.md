# SELMA Multi-State Architecture

## Design Decision

SELMA trains a separate fine-tuned model for each U.S. state plus a federal
model. Every model includes federal criminal law (Title 18 U.S.C.) as a
baseline, but each state model is additionally trained on that state's specific
criminal code.

### Rationale

1. **Legal accuracy** — Criminal law varies dramatically between states. What
   constitutes aggravated assault in Georgia (O.C.G.A. § 16-5-21) has different
   elements than in California (Cal. Penal Code § 245). A single model cannot
   reliably distinguish 50 different statutory frameworks.

2. **Reduced hallucination** — A model trained on Georgia law won't confuse
   it with Texas law. Narrow specialization reduces cross-contamination of
   legal knowledge.

3. **Jurisdictional clarity** — Law enforcement operates within specific
   jurisdictions. An officer in Georgia needs Georgia law + federal law.
   They don't need New York law cluttering the model's outputs.

4. **Update independence** — When Georgia amends its criminal code, only the
   Georgia model needs retraining. Other state models are unaffected.

5. **Deployment flexibility** — Agencies deploy only the model(s) they need.
   A state agency deploys their state model. A federal agency deploys the
   federal model. A multi-jurisdictional task force deploys multiple.

## Architecture

```
models/
├── federal/                    # 18 U.S.C. (all federal criminal law)
│   ├── config.yaml
│   └── training_data/
├── alabama/                    # Federal + Ala. Code Title 13A
│   ├── config.yaml
│   └── training_data/
├── alaska/                     # Federal + Alaska Stat. Title 11
│   ├── config.yaml
│   └── training_data/
├── ...                         # (all 50 states)
└── wyoming/                    # Federal + Wyo. Stat. Title 6
    ├── config.yaml
    └── training_data/
```

Each state model is trained on:
1. **Federal baseline** — All Title 18 U.S.C. statutory text and incident analysis examples
2. **State criminal code** — That state's specific criminal statutes
3. **State-specific synthetic examples** — Incident analyses citing state statutes

## State Criminal Codes Reference

| State | Criminal Code Citation | Code Name |
|-------|----------------------|-----------|
| Alabama | Ala. Code Title 13A | Criminal Code |
| Alaska | Alaska Stat. Title 11 | Criminal Law |
| Arizona | A.R.S. Title 13 | Criminal Code |
| Arkansas | Ark. Code Ann. Title 5 | Criminal Offenses |
| California | Cal. Penal Code | Penal Code |
| Colorado | C.R.S. Title 18 | Criminal Code |
| Connecticut | Conn. Gen. Stat. Title 53a | Penal Code |
| Delaware | Del. Code Title 11 | Crimes and Criminal Procedure |
| Florida | Fla. Stat. Title XLVI | Crimes |
| Georgia | O.C.G.A. Title 16 | Crimes and Offenses |
| Hawaii | HRS Title 37 | Hawaii Penal Code |
| Idaho | Idaho Code Title 18 | Crimes and Punishments |
| Illinois | 720 ILCS 5/ | Criminal Code of 2012 |
| Indiana | Ind. Code Title 35 | Criminal Law and Procedure |
| Iowa | Iowa Code Title XVI | Criminal Law and Procedure |
| Kansas | K.S.A. Chapter 21 | Crimes and Punishments |
| Kentucky | KRS Title L | Kentucky Penal Code |
| Louisiana | La. R.S. Title 14 | Criminal Law |
| Maine | Me. Rev. Stat. Title 17-A | Maine Criminal Code |
| Maryland | Md. Code Crim. Law | Criminal Law |
| Massachusetts | Mass. Gen. Laws Part IV | Crimes, Punishments, and Proceedings |
| Michigan | MCL Chapter 750 | Michigan Penal Code |
| Minnesota | Minn. Stat. Chapter 609 | Criminal Code |
| Mississippi | Miss. Code Ann. Title 97 | Crimes |
| Missouri | Mo. Rev. Stat. Title XXXVIII | Crimes and Punishment |
| Montana | Mont. Code Ann. Title 45 | Crimes |
| Nebraska | Neb. Rev. Stat. Chapter 28 | Crimes and Punishments |
| Nevada | NRS Title 15 | Crimes and Punishments |
| New Hampshire | N.H. RSA Title LXII | Criminal Code |
| New Jersey | N.J.S.A. Title 2C | Code of Criminal Justice |
| New Mexico | N.M. Stat. Ann. Chapter 30 | Criminal Offenses |
| New York | N.Y. Penal Law | Penal Law |
| North Carolina | N.C. Gen. Stat. Chapter 14 | Criminal Law |
| North Dakota | N.D.C.C. Title 12.1 | Criminal Code |
| Ohio | O.R.C. Title XXIX | Crimes — Procedure |
| Oklahoma | Okla. Stat. Title 21 | Crimes and Punishments |
| Oregon | ORS Title 16 | Crimes and Punishments |
| Pennsylvania | 18 Pa. C.S. | Crimes and Offenses |
| Rhode Island | R.I. Gen. Laws Title 11 | Criminal Offenses |
| South Carolina | S.C. Code Title 16 | Crimes and Offenses |
| South Dakota | S.D.C.L. Title 22 | Crimes |
| Tennessee | Tenn. Code Ann. Title 39 | Criminal Offenses |
| Texas | Tex. Penal Code | Penal Code |
| Utah | Utah Code Title 76 | Utah Criminal Code |
| Vermont | Vt. Stat. Ann. Title 13 | Crimes and Criminal Procedure |
| Virginia | Va. Code Title 18.2 | Crimes and Offenses Generally |
| Washington | RCW Title 9A | Washington Criminal Code |
| West Virginia | W. Va. Code Chapter 61 | Crimes and Their Punishment |
| Wisconsin | Wis. Stat. Chapter 939-951 | Criminal Code |
| Wyoming | Wyo. Stat. Title 6 | Crimes and Offenses |

## Training Strategy

### Phase 1: Federal Model (First)
- Train the federal-only model on Title 18 U.S.C.
- This serves as the baseline and is used by all federal agencies

### Phase 2: Priority States
- Georgia (home jurisdiction)
- California, Texas, New York, Florida (largest populations)
- States with agencies that express interest

### Phase 3: Remaining States
- Systematic rollout of remaining state models
- Community contributions for state-specific training data welcome

### Phase 4: Territories and Special Jurisdictions
- District of Columbia
- Puerto Rico, Guam, USVI, American Samoa, CNMI
- Military (UCMJ)
- Tribal jurisdictions

## Deployment Guide

Agencies deploy the model matching their jurisdiction:

```bash
# Georgia state agency
python -m src.selma.model --model models/georgia --input "incident..."

# Federal agency (FBI, DEA, etc.)
python -m src.selma.model --model models/federal --input "incident..."

# Multi-jurisdictional task force
python -m src.selma.model --model models/georgia --model models/federal --input "incident..."
```

---

*Document version: 1.0*
*Last updated: May 2026*
*Author: Ronin 48, LLC*
