#!/usr/bin/env python3
"""
Generate synthetic training data for SELMA.

Creates incident-to-charge training examples covering common criminal
scenarios for both federal (Title 18) and Georgia (Title 16) jurisdictions.

These examples teach the model to:
1. Identify applicable statutes from incident descriptions
2. Analyze elements of each offense
3. Map facts to elements
4. Classify charges by severity
"""

import json
import random
from pathlib import Path

OUTPUT_DIR = Path("data/synthetic")

# ============================================================
# SYNTHETIC TRAINING EXAMPLES
# ============================================================
# Each example is a realistic incident description paired with
# a detailed legal analysis identifying applicable statutes.

SYSTEM_PROMPT = """You are SELMA (Specified Encapsulated Limitless Memory Archive), an AI assistant \
trained to help law enforcement identify potential violations of criminal law.

Given an incident description, you will:
1. Identify all potentially applicable criminal statutes (federal and/or state)
2. For each statute, list the required elements of the offense
3. Map the facts of the incident to each element
4. Classify the potential charge (felony/misdemeanor, degree)
5. Note any jurisdictional considerations
6. Flag related or lesser included offenses

Always cite specific statute numbers. Be thorough but precise.
If the facts are insufficient to support a charge, explain what additional \
information would be needed.

DISCLAIMER: This analysis is for investigative assistance only and does not \
constitute legal advice. All conclusions should be reviewed by qualified legal counsel."""


SYNTHETIC_EXAMPLES = [
    # === FEDERAL: BANK ROBBERY ===
    {
        "messages": [
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": """Analyze the following incident for potential criminal violations:

Two masked individuals entered First National Bank at approximately 2:30 PM on March 15. Subject 1 approached the teller counter and displayed a semi-automatic handgun, demanding all cash from the drawers. Subject 2 remained near the entrance, blocking customers from leaving. The teller complied and handed over approximately $47,000. Both subjects fled in a dark-colored sedan. No injuries were reported. The bank is FDIC-insured."""},
            {"role": "assistant", "content": """## Criminal Law Analysis

### Potential Violations Identified

#### 1. 18 U.S.C. § 2113(a) — Bank Robbery

**Severity:** Felony (up to 20 years imprisonment)

**Elements of the Offense:**
1. **Taking or attempting to take property** — Subjects took approximately $47,000 in cash from the teller
2. **From a bank, credit union, or savings and loan** — First National Bank (FDIC-insured, establishing federal jurisdiction)
3. **By force and violence, or intimidation** — Subject 1 displayed a semi-automatic handgun and made demands; Subject 2 blocked the exit, creating intimidation

**All elements appear satisfied by the facts.**

#### 2. 18 U.S.C. § 2113(d) — Armed Bank Robbery

**Severity:** Felony (up to 25 years imprisonment)

**Elements of the Offense:**
1. All elements of § 2113(a) — Satisfied as above
2. **Assault or jeopardy of life with a dangerous weapon** — Subject 1 displayed a semi-automatic handgun, placing the teller and customers in jeopardy

**All elements appear satisfied. This is the aggravated form of bank robbery.**

#### 3. 18 U.S.C. § 924(c)(1)(A) — Use of Firearm During a Crime of Violence

**Severity:** Felony (minimum 5 years consecutive; 7 years if brandished)

**Elements of the Offense:**
1. **Possession/use of a firearm** — Subject 1 displayed a semi-automatic handgun
2. **During and in relation to a crime of violence** — Bank robbery under § 2113 is a crime of violence
3. **Brandishing** — The firearm was displayed/shown to the teller, meeting the definition of "brandishing" (7-year mandatory minimum)

**All elements appear satisfied.**

#### 4. 18 U.S.C. § 2 — Aiding and Abetting / Principals

**Severity:** Same as underlying offense

**Application:** Subject 2, who blocked the entrance and prevented customers from leaving, is liable as a principal under § 2 for all offenses committed by Subject 1. Standing guard and facilitating the robbery constitutes aiding and abetting.

#### 5. 18 U.S.C. § 371 — Conspiracy

**Severity:** Felony (up to 5 years)

**Elements:**
1. **Agreement between two or more persons** — The coordinated actions (one at counter, one at door) demonstrate prior agreement
2. **To commit an offense against the United States** — Bank robbery
3. **Overt act in furtherance** — Entering the bank, displaying the weapon, demanding money

**All elements appear satisfied.**

### Jurisdictional Notes
- **Federal jurisdiction** is established because the bank is FDIC-insured, bringing it under 18 U.S.C. § 2113
- State charges (robbery, armed robbery, conspiracy) may also apply depending on the state where the bank is located
- Federal prosecution is typical for FDIC-insured bank robberies

### Lesser Included Offenses
- 18 U.S.C. § 2113(a) simple bank robbery (lesser included of § 2113(d))
- Attempted bank robbery if any element of completion is challenged

### Additional Information Needed
- Exact location (state) for potential parallel state charges
- Whether the firearm was loaded (relevant to sentencing)
- Vehicle identification for potential interstate flight charges (18 U.S.C. § 1073)
- Whether any dye packs or tracking devices were in the cash

### Summary
This incident presents strong probable cause for federal bank robbery charges under 18 U.S.C. § 2113(a) and (d), use of a firearm during a crime of violence under § 924(c), conspiracy under § 371, and aiding and abetting under § 2. Both subjects face identical charges. The mandatory minimum for the firearm charge alone is 7 years consecutive to any other sentence."""}
        ],
        "type": "incident_analysis",
        "jurisdiction": "federal",
        "statutes_referenced": ["18 U.S.C. § 2113(a)", "18 U.S.C. § 2113(d)", "18 U.S.C. § 924(c)", "18 U.S.C. § 2", "18 U.S.C. § 371"],
    },

    # === GEORGIA: AGGRAVATED ASSAULT ===
    {
        "messages": [
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": """Analyze the following incident for potential criminal violations:

On Saturday night at approximately 11:45 PM, officers responded to a disturbance at a bar on Peachtree Street in Atlanta, Georgia. Witnesses reported that the suspect, a 34-year-old male, struck the victim in the head with a glass bottle during an argument. The victim sustained a deep laceration above the left eye requiring 15 stitches and reported temporary vision impairment. The suspect was detained at the scene. Witnesses stated the argument began over a disputed bar tab. The suspect showed signs of intoxication."""},
            {"role": "assistant", "content": """## Criminal Law Analysis

### Potential Violations Identified

#### 1. O.C.G.A. § 16-5-21(a)(2) — Aggravated Assault

**Severity:** Felony (1 to 20 years imprisonment)

**Elements of the Offense:**
1. **An assault** — The suspect committed an act of violence against the victim
2. **With a deadly weapon or object which, when used offensively, is likely to result in serious bodily injury** — A glass bottle, when swung at a person's head, is an object likely to result in serious bodily injury. Georgia courts have consistently held that bottles used as weapons qualify under this subsection
3. **Without intent to murder** — The facts suggest an impulsive act during an argument, not premeditated intent to kill

**All elements appear satisfied.**

#### 2. O.C.G.A. § 16-5-24(a) — Aggravated Battery

**Severity:** Felony (1 to 20 years imprisonment)

**Elements of the Offense:**
1. **Maliciously causing bodily harm to another** — Striking the victim in the head with a bottle
2. **By depriving the victim of a member of the body** — The temporary vision impairment could qualify if the eye damage is lasting
3. **By rendering a member of the body useless** — Temporary vision impairment in the left eye
4. **By seriously disfiguring the body** — A deep laceration requiring 15 stitches above the eye likely constitutes serious disfigurement

**Elements likely satisfied, particularly under the "seriously disfiguring" prong. The "rendering useless" prong depends on whether the vision impairment is permanent.**

#### 3. O.C.G.A. § 16-5-20(a)(1) — Simple Assault (Lesser Included)

**Severity:** Misdemeanor (up to 12 months, $1,000 fine)

**Elements:**
1. **Attempting to commit a violent injury to another** — Satisfied
2. **Or committing an act which places another in reasonable apprehension of immediately receiving a violent injury** — Satisfied

**This is a lesser included offense of aggravated assault.**

#### 4. O.C.G.A. § 16-5-23(a) — Simple Battery (Lesser Included)

**Severity:** Misdemeanor (up to 12 months, $1,000 fine)

**Elements:**
1. **Intentionally making physical contact of an insulting or provoking nature** — OR
2. **Intentionally causing physical harm to another** — Striking with the bottle caused physical harm

**This is a lesser included offense of aggravated battery.**

#### 5. O.C.G.A. § 16-11-39(a) — Disorderly Conduct

**Severity:** Misdemeanor (up to 12 months, $1,000 fine)

**Elements:**
1. **Acting in a violent or tumultuous manner** toward another person, such that the person is placed in reasonable fear for their safety
2. The altercation in a public bar constitutes disorderly conduct

**Elements satisfied.**

### Jurisdictional Notes
- All charges fall under **Georgia state jurisdiction** (Fulton County)
- The incident occurred in the City of Atlanta; APD has primary jurisdiction
- No federal nexus is apparent from the facts presented
- Venue: Fulton County Superior Court (felonies) or State/Magistrate Court (misdemeanors)

### Lesser Included Offenses
- O.C.G.A. § 16-5-20 Simple Assault (lesser included of Aggravated Assault)
- O.C.G.A. § 16-5-23 Simple Battery (lesser included of Aggravated Battery)

### Sentencing Considerations
- Intoxication is generally **not** a defense under Georgia law (O.C.G.A. § 16-3-4), though voluntary intoxication may be relevant to specific intent crimes
- Prior criminal history may affect sentencing range
- Restitution for medical expenses is likely

### Additional Information Needed
- Suspect's prior criminal history (affects sentencing, repeat offender status)
- Medical prognosis for the victim's vision impairment (permanent vs. temporary affects aggravated battery charge)
- Whether the suspect has any defensive injuries suggesting mutual combat
- Surveillance footage from the bar
- BAC level of the suspect if tested

### Summary
The primary charges supported by these facts are **Aggravated Assault** under O.C.G.A. § 16-5-21(a)(2) and **Aggravated Battery** under O.C.G.A. § 16-5-24(a). Both are felonies carrying 1–20 years imprisonment. The glass bottle constitutes a deadly weapon/dangerous instrument when used to strike someone in the head. The 15-stitch laceration and vision impairment support the aggravated battery charge under the "serious disfigurement" prong. The suspect's intoxication is not a valid defense under Georgia law."""}
        ],
        "type": "incident_analysis",
        "jurisdiction": "georgia",
        "statutes_referenced": ["O.C.G.A. § 16-5-21(a)(2)", "O.C.G.A. § 16-5-24(a)", "O.C.G.A. § 16-5-20(a)(1)", "O.C.G.A. § 16-5-23(a)", "O.C.G.A. § 16-11-39(a)"],
    },

    # === FEDERAL: WIRE FRAUD / IDENTITY THEFT ===
    {
        "messages": [
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": """Analyze the following incident for potential criminal violations:

An investigation by the FBI Cyber Division revealed that a suspect operating from Marietta, Georgia created approximately 200 fraudulent websites mimicking legitimate financial institutions. The suspect used phishing emails sent to thousands of victims across 15 states to harvest login credentials, Social Security numbers, and banking information. Using the stolen information, the suspect made unauthorized wire transfers totaling approximately $1.2 million over an 8-month period. The suspect also opened 47 credit card accounts in victims' names and made purchases totaling $340,000. Evidence was found on the suspect's computer including databases of stolen personal information for approximately 12,000 individuals."""},
            {"role": "assistant", "content": """## Criminal Law Analysis

### Potential Violations Identified

#### 1. 18 U.S.C. § 1343 — Wire Fraud

**Severity:** Felony (up to 20 years; up to 30 years if affecting a financial institution)

**Elements of the Offense:**
1. **A scheme or artifice to defraud** — Creating 200 fraudulent websites mimicking financial institutions and sending phishing emails constitutes a scheme to defraud
2. **Using interstate wire communications** — Phishing emails sent across 15 states; unauthorized wire transfers conducted electronically
3. **With intent to defraud** — The systematic nature of the operation demonstrates intent
4. **Material misrepresentation** — Fraudulent websites designed to deceive victims into believing they were legitimate financial institutions

**All elements satisfied. The 30-year enhancement likely applies as the scheme affected financial institutions.**

#### 2. 18 U.S.C. § 1028(a)(7) — Aggravated Identity Theft / Fraud in Connection with Identification Documents

**Severity:** Felony (up to 15 years)

**Elements:**
1. **Knowingly producing, transferring, or possessing** identification documents or means of identification
2. **With intent to defraud** — Using stolen SSNs and banking info to open accounts and make transfers
3. **Affects interstate commerce** — Victims across 15 states

**All elements satisfied.**

#### 3. 18 U.S.C. § 1028A — Aggravated Identity Theft

**Severity:** Felony (mandatory 2 years consecutive, no probation)

**Elements:**
1. **During and in relation to a predicate felony** — Wire fraud, bank fraud, and access device fraud are all predicate felonies
2. **Knowingly possessing, transferring, or using the means of identification of another person** — SSNs, banking credentials of 12,000+ individuals

**All elements satisfied. This carries a mandatory 2-year consecutive sentence.**

#### 4. 18 U.S.C. § 1344 — Bank Fraud

**Severity:** Felony (up to 30 years, $1M fine)

**Elements:**
1. **Knowingly executing a scheme to defraud a financial institution** — Unauthorized wire transfers from victim bank accounts
2. **Or to obtain money or property from a financial institution by false pretenses** — Using stolen credentials to access accounts

**All elements satisfied.**

#### 5. 18 U.S.C. § 1029(a)(2) — Fraud with Access Devices (Credit Cards)

**Severity:** Felony (up to 15 years per count)

**Elements:**
1. **Knowingly and with intent to defraud** — Opening fraudulent credit card accounts
2. **Using unauthorized access devices** — 47 credit card accounts opened in victims' names
3. **Obtaining anything of value aggregating $1,000 or more** — $340,000 in purchases

**All elements satisfied. Each fraudulently opened account could be a separate count.**

#### 6. 18 U.S.C. § 1030(a)(2) — Computer Fraud and Abuse Act (CFAA)

**Severity:** Felony (up to 5 years for first offense; up to 10 years for subsequent)

**Elements:**
1. **Intentionally accessing a computer without authorization** — Accessing victims' financial accounts using stolen credentials
2. **Obtaining information from a financial institution** — Banking information, account data

**All elements satisfied.**

#### 7. 18 U.S.C. § 1956 — Money Laundering

**Severity:** Felony (up to 20 years)

**Elements:**
1. **Conducting financial transactions** — Wire transfers totaling $1.2M, credit card purchases of $340K
2. **Involving proceeds of specified unlawful activity** — Wire fraud, bank fraud, identity theft
3. **Knowing the transactions were designed to conceal the nature or source** — Using victims' identities to move and spend stolen funds

**Elements likely satisfied depending on how the funds were moved/spent.**

#### 8. O.C.G.A. § 16-9-121 — Georgia Computer Theft / Invasion of Privacy

**Severity:** Felony under Georgia law (1–15 years)

**Elements:**
1. **Computer theft** — Using computers to commit theft through deception
2. **Computer invasion of privacy** — Accessing personal data without authorization

**Georgia state charges may apply in addition to federal charges since the suspect operated from Marietta, GA.**

#### 9. O.C.G.A. § 16-9-31 — Financial Identity Fraud (Georgia)

**Severity:** Felony (1–10 years)

**Elements:**
1. **Using identifying information of another person** without consent
2. **To obtain or attempt to obtain credit, money, goods, or services** in the name of another

**State charges may be pursued alongside federal prosecution.**

### Jurisdictional Notes
- **Primary jurisdiction: Federal** — The interstate nature (15 states), use of wire communications, FDIC-insured banks, and involvement of the U.S. mail system firmly establish federal jurisdiction
- FBI Cyber Division is the lead investigative agency
- **Venue** could be established in any district where victims reside or where wire communications originated/terminated
- Georgia state charges may be pursued concurrently (suspect operated from Marietta, Cobb County)

### Sentencing Considerations
- Federal Sentencing Guidelines loss amount ($1.54M+) significantly increases the offense level
- Number of victims (12,000+) triggers enhancement under USSG § 2B1.1(b)(2)
- Sophisticated means enhancement likely under USSG § 2B1.1(b)(10)
- Aggravated identity theft carries mandatory 2-year consecutive sentence
- Restitution to all victims will be ordered

### Additional Information Needed
- Whether the suspect acted alone or as part of a larger organization (conspiracy charges)
- How the wire transfers were routed (additional money laundering evidence)
- Whether any victims were elderly (elder fraud enhancement)
- Whether any government identification was compromised (additional charges)
- Full forensic analysis of the computer databases

### Summary
This case presents a massive multi-count federal prosecution. The primary charges include **Wire Fraud** (§ 1343), **Bank Fraud** (§ 1344), **Aggravated Identity Theft** (§ 1028A, mandatory 2 years consecutive), **Access Device Fraud** (§ 1029), and **Computer Fraud** (§ 1030). With 12,000+ victims across 15 states, loss amounts exceeding $1.5M, and 47 fraudulent accounts, the Federal Sentencing Guidelines likely yield a range of 10–20+ years. Georgia state charges for computer theft and financial identity fraud may also be pursued."""}
        ],
        "type": "incident_analysis",
        "jurisdiction": "both",
        "statutes_referenced": ["18 U.S.C. § 1343", "18 U.S.C. § 1028(a)(7)", "18 U.S.C. § 1028A", "18 U.S.C. § 1344", "18 U.S.C. § 1029(a)(2)", "18 U.S.C. § 1030(a)(2)", "18 U.S.C. § 1956", "O.C.G.A. § 16-9-121", "O.C.G.A. § 16-9-31"],
    },

    # === GEORGIA: BURGLARY / THEFT ===
    {
        "messages": [
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": """Analyze the following incident for potential criminal violations:

Homeowner in Decatur, Georgia returned from vacation to find the back door of their residence forced open. Missing items include: a 65-inch television ($1,200), a laptop computer ($2,000), assorted jewelry ($5,000 estimated), a legally owned Glock 19 handgun ($550), and approximately $800 in cash. Total estimated loss: $9,550. Neighbors report seeing an unfamiliar white van parked in the driveway two days prior. Security camera from a neighboring house captured footage of a single male individual carrying items from the residence to the van. The suspect was wearing gloves."""},
            {"role": "assistant", "content": """## Criminal Law Analysis

### Potential Violations Identified

#### 1. O.C.G.A. § 16-7-1(b) — Burglary in the First Degree

**Severity:** Felony (1 to 20 years imprisonment)

**Elements of the Offense:**
1. **Without authority** — Suspect had no authorization to enter the dwelling
2. **Entering or remaining within** — Forced entry through the back door demonstrates unauthorized entry
3. **A dwelling house of another** — The residence is a dwelling house (owner was away on vacation but it remains their dwelling)
4. **With the intent to commit a felony or theft therein** — The theft of $9,550 in property demonstrates intent to commit theft

**All elements satisfied. First degree burglary applies because the structure is a dwelling house.**

Note: Under Georgia law, a "dwelling house" includes any building designed for sleeping purposes, regardless of whether the occupant is present at the time. O.C.G.A. § 16-7-1(c).

#### 2. O.C.G.A. § 16-8-2 — Theft by Taking (Felony)

**Severity:** Felony (1 to 10 years, because value exceeds $5,000 but is under $25,000 per O.C.G.A. § 16-8-12(a)(1))

**Elements of the Offense:**
1. **Unlawfully taking** — Removing property from the residence
2. **Property of another** — Items belonging to the homeowner
3. **With the intention of depriving the owner** — Suspect removed items from the premises in a van, demonstrating intent to permanently deprive
4. **Value exceeds $5,000** — Total estimated loss of $9,550 makes this a felony

**All elements satisfied.**

#### 3. O.C.G.A. § 16-11-131(b) — Theft of a Firearm

**Severity:** Felony (1 to 10 years)

**Elements of the Offense:**
1. **Committing the offense of theft** of a firearm — The Glock 19 handgun was stolen
2. **The item is a firearm** — Glock 19 is a firearm as defined under Georgia law

**All elements satisfied. This is charged separately from general theft.**

#### 4. O.C.G.A. § 16-7-1(a) — Burglary in the Second Degree (Lesser Included)

**Severity:** Felony (1 to 5 years)

**Elements:** Same as first degree but applies to non-dwelling structures. This is a lesser included offense if the dwelling house element is contested.

#### 5. O.C.G.A. § 16-7-2 — Smash and Grab Burglary / Criminal Damage to Property in the Second Degree

**Severity:** Misdemeanor (up to 12 months)

**Elements:**
1. **Intentionally damaging property of another** — The forced entry through the back door caused damage
2. **Without consent** — Owner did not authorize the damage

**Satisfied as an additional charge for the damaged door.**

#### 6. O.C.G.A. § 16-8-18 — Entering Automobile (if applicable to the van)

**Note:** If further investigation reveals the suspect used a stolen vehicle, additional charges would apply.

### Jurisdictional Notes
- **Georgia state jurisdiction** — DeKalb County
- Primary law enforcement: DeKalb County Police Department
- Venue: DeKalb County Superior Court (felonies)
- The stolen firearm should be reported to ATF/NCIC — if the firearm crosses state lines, federal charges under 18 U.S.C. § 922(j) (possession of stolen firearm) may apply

### Sentencing Considerations
- First degree burglary carries 1–20 years; this range is substantial
- Multiple felony charges may be run consecutively
- If the suspect has prior burglary convictions, enhanced sentencing applies
- Wearing gloves suggests premeditation and sophistication
- Georgia has mandatory minimum sentences for certain repeat property offenders

### Additional Information Needed
- Forensic analysis of the forced entry point (tool marks, DNA)
- Canvass for additional security camera footage to identify the van (plates, make/model)
- Whether any latent fingerprints were recovered despite gloves
- Serial number of the stolen Glock 19 for NCIC entry
- Whether any of the stolen items have appeared at pawn shops (O.C.G.A. § 16-8-5 — Theft by Receiving)
- Suspect identification from the neighbor's security footage
- Cell tower data for the area during the estimated time of the crime

### Summary
The primary charges are **Burglary in the First Degree** (O.C.G.A. § 16-7-1(b), felony, 1–20 years) and **Felony Theft by Taking** (O.C.G.A. § 16-8-2, 1–10 years for $9,550 total value). The **Theft of a Firearm** charge (O.C.G.A. § 16-11-131(b)) is particularly significant and should trigger notification to ATF. The use of gloves and a van suggest a deliberate, planned operation. Investigation should focus on identifying the suspect from the neighbor's camera footage and tracking the stolen items."""}
        ],
        "type": "incident_analysis",
        "jurisdiction": "georgia",
        "statutes_referenced": ["O.C.G.A. § 16-7-1(b)", "O.C.G.A. § 16-8-2", "O.C.G.A. § 16-11-131(b)", "O.C.G.A. § 16-7-1(a)", "O.C.G.A. § 16-7-2"],
    },

    # === FEDERAL: DRUG TRAFFICKING ===
    {
        "messages": [
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": """Analyze the following incident for potential criminal violations:

DEA and local task force officers executed a search warrant at a residence in Savannah, Georgia. During the search they recovered: 2 kilograms of cocaine, 500 grams of fentanyl, a pill press with tooling for making counterfeit oxycodone tablets, approximately 10,000 counterfeit pills, three firearms (two handguns and one AR-15 style rifle), $85,000 in U.S. currency in a floor safe, multiple cell phones, a money counter, digital scales, and packaging materials. Two individuals were present at the residence. Subject 1 is the registered owner of the property. Subject 2 is a known associate with two prior felony drug convictions. A K-9 alerted on a vehicle parked outside which contained an additional 500 grams of cocaine and drug ledgers."""},
            {"role": "assistant", "content": """## Criminal Law Analysis

### Potential Violations Identified

#### 1. 21 U.S.C. § 841(a)(1) — Possession with Intent to Distribute Controlled Substances

**Severity:** Felony

For Cocaine (2.5 kg total):
- 21 U.S.C. § 841(b)(1)(B): 500g–5kg of cocaine = **5–40 years** (10–life if prior felony drug conviction applies to Subject 2)

For Fentanyl (500g):
- 21 U.S.C. § 841(b)(1)(A): 400g+ of fentanyl = **10 years to life** (mandatory minimum; **20 years to life** for Subject 2 with prior convictions)

**Elements:**
1. **Knowing or intentional possession** — Substances found at residence and in vehicle
2. **Of a controlled substance** — Cocaine (Schedule II), Fentanyl (Schedule II)
3. **With intent to distribute** — Intent established by: quantity far exceeding personal use, packaging materials, digital scales, money counter, pill press, drug ledgers, $85K cash

**All elements satisfied for both subjects. Constructive possession applies.**

#### 2. 21 U.S.C. § 841(a)(1) — Manufacturing Counterfeit Controlled Substances

**Severity:** Felony (same as distribution of the substance being counterfeited)

**Elements:**
1. **Manufacturing** — Pill press with oxycodone tooling and 10,000 counterfeit pills constitute manufacturing
2. **Counterfeit controlled substance** — Pills designed to mimic oxycodone

**All elements satisfied. If pills contain fentanyl, this becomes distribution of fentanyl under false pretenses — an aggravating factor.**

#### 3. 18 U.S.C. § 924(c)(1) — Possession of Firearms in Furtherance of Drug Trafficking

**Severity:** Felony (minimum 5 years consecutive; 7 years if brandished; 10 years if discharged)

**Elements:**
1. **Possession of a firearm** — Three firearms recovered (two handguns, one AR-15)
2. **In furtherance of a drug trafficking crime** — Firearms co-located with narcotics, cash, and distribution paraphernalia at the same residence

**All elements satisfied. Each firearm may be a separate count. The AR-15 may trigger additional firearms charges.**

#### 4. 18 U.S.C. § 922(g)(1) — Felon in Possession of a Firearm

**Severity:** Felony (up to 15 years)

**Applies to Subject 2** (two prior felony drug convictions):
1. **Previously convicted of a felony** — Two prior felony drug convictions
2. **Possessed a firearm** — Constructive possession of firearms found in the residence

**Elements satisfied for Subject 2. Subject 2 may also qualify for Armed Career Criminal enhancement (18 U.S.C. § 924(e)) if prior convictions qualify — mandatory minimum 15 years.**

#### 5. 21 U.S.C. § 846 — Conspiracy to Distribute Controlled Substances

**Severity:** Same as the underlying offense (up to life imprisonment)

**Elements:**
1. **Agreement between two or more persons** — Two subjects present with distribution infrastructure
2. **To violate federal drug laws** — Manufacturing and distributing cocaine, fentanyl, and counterfeit pills
3. **Overt act** — Possession of drugs, press, packaging, ledgers

**All elements satisfied.**

#### 6. 18 U.S.C. § 1956/1957 — Money Laundering

**Severity:** Felony (up to 20 years for § 1956; up to 10 years for § 1957)

**Elements:**
1. **Financial transactions involving proceeds of unlawful activity** — $85,000 in cash in a floor safe
2. **Knowledge that the property involved proceeds of unlawful activity** — Cash co-located with narcotics and distribution infrastructure
3. **Money counter** suggests systematic handling of drug proceeds

**Elements likely satisfied. Structuring charges (31 U.S.C. § 5324) may also apply if bank deposits were made in amounts under $10,000.**

#### 7. O.C.G.A. § 16-13-31(a)(1) — Trafficking in Cocaine (Georgia)

**Severity:** Felony

- 2,500g (2.5 kg) total cocaine = **25 years mandatory, $1,000,000 fine** (over 400g threshold)

#### 8. O.C.G.A. § 16-13-31.1 — Trafficking in Fentanyl (Georgia)

**Severity:** Felony

- 500g fentanyl triggers severe mandatory minimum under Georgia trafficking statute

#### 9. 21 U.S.C. § 856 — Maintaining Drug-Involved Premises

**Severity:** Felony (up to 20 years)

**Applies to Subject 1** as registered property owner:
1. **Knowingly opening, maintaining, or managing a place** — Subject 1 owns the property
2. **For the purpose of manufacturing, distributing, or using controlled substances** — Residence used as drug manufacturing and storage facility

**All elements satisfied for Subject 1.**

### Jurisdictional Notes
- **Dual jurisdiction** — Both federal and Georgia state charges apply
- Federal prosecution likely takes priority given DEA involvement and quantities
- Southern District of Georgia (Savannah Division) for federal charges
- Chatham County for state charges
- Subject 2's prior convictions trigger significant federal enhancements

### Sentencing Considerations
- **Subject 2 faces potential life imprisonment** due to prior felony drug convictions (21 U.S.C. § 851 enhancement) combined with fentanyl quantity
- **Subject 1** faces 10+ years mandatory minimum on fentanyl charges alone, plus 5 years consecutive for § 924(c)
- Federal Sentencing Guidelines will calculate based on combined drug weight (converted to marijuana equivalents)
- Fentanyl's lethality may result in upward departure
- Counterfeit pill operation targeting opioid users is an aggravating factor
- Forfeiture: $85,000 cash, firearms, vehicle, and potentially the residence under 21 U.S.C. § 853

### Additional Information Needed
- Lab analysis confirming substance identity and purity
- Whether counterfeit pills contain fentanyl (dramatically increases danger and sentencing)
- Subject 2's specific prior convictions for § 851 enhancement
- Cell phone and ledger analysis for co-conspirators
- Financial records, bank accounts, cryptocurrency wallets
- Source of supply investigation
- Whether any overdose deaths are linked to this operation (21 U.S.C. § 841(b)(1)(A) death enhancement — mandatory 20 years to life)

### Summary
This is a major federal drug trafficking case. The combination of **2.5 kg cocaine, 500g fentanyl, counterfeit pill manufacturing, three firearms, and $85K cash** represents a significant distribution operation. Primary federal charges include **Possession with Intent to Distribute** (§ 841), **Manufacturing** (§ 841), **Firearms in Drug Trafficking** (§ 924(c)), **Conspiracy** (§ 846), and **Drug Premises** (§ 856). Subject 2 faces potential **life imprisonment** due to prior convictions. Georgia trafficking charges provide additional mandatory minimums. The counterfeit fentanyl-laced pill operation poses extreme public health danger and will likely be an aggravating factor at sentencing."""}
        ],
        "type": "incident_analysis",
        "jurisdiction": "both",
        "statutes_referenced": ["21 U.S.C. § 841(a)(1)", "21 U.S.C. § 841(b)(1)(A)", "21 U.S.C. § 841(b)(1)(B)", "18 U.S.C. § 924(c)(1)", "18 U.S.C. § 922(g)(1)", "21 U.S.C. § 846", "18 U.S.C. § 1956", "O.C.G.A. § 16-13-31(a)(1)", "O.C.G.A. § 16-13-31.1", "21 U.S.C. § 856"],
    },

    # === GEORGIA: DOMESTIC VIOLENCE / STALKING ===
    {
        "messages": [
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": """Analyze the following incident for potential criminal violations:

A woman in Gwinnett County, Georgia filed a police report stating her ex-boyfriend has been engaging in the following behavior over the past three months since their breakup: (1) Showing up uninvited at her workplace at least 12 times, (2) Sending over 200 text messages per day despite being told to stop, (3) Creating fake social media accounts to monitor her activity after being blocked, (4) Placing a GPS tracking device on her vehicle without her knowledge (discovered by her mechanic), (5) On the most recent occasion, he followed her from work to her home and pounded on her door screaming threats that he would "make her regret leaving" and "she wouldn't be safe anywhere." A neighbor called 911. The victim has documented all text messages and has screenshots of the fake social media accounts."""},
            {"role": "assistant", "content": """## Criminal Law Analysis

### Potential Violations Identified

#### 1. O.C.G.A. § 16-5-90(a) — Stalking

**Severity:** Misdemeanor for first offense (up to 12 months, $1,000 fine); **Felony** for second conviction or violation of protective order (1–10 years)

**Elements of the Offense:**
1. **Following, placing under surveillance, or contacting another person** — All three are present: following from work to home, GPS surveillance on vehicle, 200+ daily texts and fake social media monitoring
2. **At or about a place or places without the consent of the other person** — Victim has told suspect to stop; she blocked him on social media
3. **For the purpose of harassing and intimidating** — Pattern of behavior over three months with escalating intensity
4. **Causing emotional distress** — The volume and nature of contact (200 texts/day, workplace appearances, GPS tracking, threats) would cause a reasonable person substantial emotional distress

**All elements satisfied. This is a strong stalking case with extensive documentation.**

#### 2. O.C.G.A. § 16-5-91(a) — Aggravated Stalking

**Severity:** Felony (1 to 10 years, $10,000 fine)

**Elements:**
1. **Stalking as defined in § 16-5-90** — Satisfied as above
2. **In violation of a temporary restraining order, temporary protective order, permanent restraining order, permanent protective order, preliminary injunction, or good behavior bond** — If a protective order exists, OR
3. **Making contact in a manner that causes the victim to reasonably fear for their safety or the safety of a family member** — The threats ("make her regret leaving," "she wouldn't be safe anywhere") constitute threats that would cause a reasonable person to fear for their safety

**If no protective order exists, pursue under element 3 — the explicit threats satisfy this element.**

#### 3. O.C.G.A. § 16-5-20(a)(2) — Simple Assault (Threat)

**Severity:** Misdemeanor (up to 12 months, $1,000 fine)

**Elements:**
1. **Committing an act which places another in reasonable apprehension of immediately receiving a violent injury** — "Make her regret leaving" and "she wouldn't be safe anywhere" while pounding on her door constitute threats placing the victim in reasonable apprehension of imminent harm

**Elements satisfied based on the doorstep confrontation.**

#### 4. O.C.G.A. § 16-5-23.1 — Battery (Family Violence)

**Severity:** Misdemeanor (up to 12 months); Felony on third or subsequent conviction

**Note:** While no physical contact is described in this incident, if during the doorstep confrontation any physical contact occurred (even touching), family violence battery would apply since they are former intimate partners under O.C.G.A. § 19-13-1.

#### 5. O.C.G.A. § 16-5-94 — Criminal Surveillance / Invasion of Privacy (GPS Tracker)

**Severity:** Misdemeanor to Felony depending on circumstances

**Elements:**
1. **Installing a tracking device on another person's vehicle** without consent
2. **For the purpose of monitoring the person's movements**

**The GPS tracker placed on the victim's vehicle without knowledge or consent constitutes criminal surveillance.**

#### 6. O.C.G.A. § 16-11-39.1(a) — Harassing Communications

**Severity:** Misdemeanor (up to 12 months)

**Elements:**
1. **Contact by telephone, text, or electronic means** — 200+ texts per day, fake social media accounts
2. **For the purpose of harassing, molesting, threatening, or intimidating** — Volume and persistence after being told to stop
3. **Without a legitimate purpose** — No legitimate reason for 200 daily texts to someone who has demanded no contact

**All elements satisfied.**

#### 7. O.C.G.A. § 16-11-66.1 — Computer or Electronic Surveillance / Tracking without Consent

**Severity:** Misdemeanor or Felony

**Elements:**
1. **Using electronic tracking device** — GPS tracker installed on victim's vehicle
2. **Without consent of the person being tracked** — Victim unaware until mechanic discovered it
3. **Not authorized by law** — No legal authority to track ex-girlfriend

**All elements satisfied.**

#### 8. O.C.G.A. § 16-9-93.1 — Identity Fraud (Fake Social Media Accounts)

**Severity:** Varies

**Note:** Creating fake social media accounts to circumvent being blocked could constitute fraud or impersonation depending on how the accounts were set up. If fake accounts used another person's identity or photos, additional charges may apply.

### Jurisdictional Notes
- **Georgia state jurisdiction** — Gwinnett County
- Primary law enforcement: Gwinnett County Police Department
- Venue: Gwinnett County State/Superior Court
- **No federal nexus** unless the GPS device was purchased/shipped interstate in furtherance of stalking (18 U.S.C. § 2261A — Federal Interstate Stalking — could apply if any communications crossed state lines)
- The victim should immediately seek a **Temporary Protective Order (TPO)** under O.C.G.A. § 16-5-94

### Immediate Safety Recommendations
- Assist victim in obtaining an emergency Temporary Protective Order
- Document and preserve all electronic evidence (texts, social media screenshots)
- Recover the GPS device for forensic analysis (fingerprints, purchase records)
- Conduct a safety assessment of victim's residence and workplace
- Consider whether the suspect has access to firearms

### Sentencing Considerations
- Aggravated stalking is the most serious charge and should be the lead
- Multiple charges can run consecutively
- A protective order violation would enhance future violations to automatic felony
- Pattern of behavior over 3 months demonstrates persistence and escalation
- Documented threats of violence ("she wouldn't be safe anywhere") are particularly concerning for victim safety assessment

### Additional Information Needed
- Whether any protective orders currently exist (would elevate to aggravated stalking)
- Suspect's prior criminal history (prior stalking or DV convictions)
- Whether suspect owns or has access to firearms (lethality assessment)
- Whether suspect has made similar threats to others
- Origin/purchase records of the GPS tracking device
- Whether the suspect has violated any workplace no-trespass orders
- Full forensic extraction of victim's phone for text message records
- IP address records for the fake social media accounts

### Summary
This is a serious **stalking and harassment** case with multiple felony-level charges. The primary charge should be **Aggravated Stalking** (O.C.G.A. § 16-5-91) based on the explicit threats made at the victim's home. Supporting charges include **Stalking** (§ 16-5-90), **Simple Assault** (§ 16-5-20), **Harassing Communications** (§ 16-11-39.1), and **Unauthorized Tracking** (§ 16-11-66.1). The GPS tracker, 200+ daily texts, 12 workplace visits, fake accounts, and escalating threats demonstrate a clear pattern of dangerous obsessive behavior. Immediate priority should be victim safety through a Temporary Protective Order and assessment of the suspect's access to firearms."""}
        ],
        "type": "incident_analysis",
        "jurisdiction": "georgia",
        "statutes_referenced": ["O.C.G.A. § 16-5-90(a)", "O.C.G.A. § 16-5-91(a)", "O.C.G.A. § 16-5-20(a)(2)", "O.C.G.A. § 16-5-23.1", "O.C.G.A. § 16-5-94", "O.C.G.A. § 16-11-39.1(a)", "O.C.G.A. § 16-11-66.1", "O.C.G.A. § 16-9-93.1"],
    },

    # === FEDERAL: TERRORISM / THREATS ===
    {
        "messages": [
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": """Analyze the following incident for potential criminal violations:

The FBI Joint Terrorism Task Force received a tip about a 22-year-old male in Rome, Georgia who posted a manifesto on an online forum detailing plans to attack a federal courthouse. Investigation revealed he had purchased an AR-15 rifle two weeks ago, acquired 1,000 rounds of ammunition, and had conducted surveillance of the Richard B. Russell Federal Building in Atlanta (a federal building housing federal courts). His internet history showed extensive research on building layouts, security guard schedules, and past attacks on government buildings. He had also communicated with an overseas individual who provided encouragement and tactical advice. When agents executed a search warrant, they found the rifle, ammunition, body armor, a hand-drawn map of the building, and notes on security vulnerabilities."""},
            {"role": "assistant", "content": """## Criminal Law Analysis

### Potential Violations Identified

#### 1. 18 U.S.C. § 2332a — Use of Weapons of Mass Destruction (Attempted)

**Severity:** Felony (up to life imprisonment)

**Note:** While an AR-15 alone may not constitute a WMD, if the investigation reveals any explosive components or plans to create explosive devices, this statute applies. Reserved pending further investigation.

#### 2. 18 U.S.C. § 1361 — Destruction of Government Property (Attempted/Conspiracy)

**Severity:** Felony (up to 10 years if damage exceeds $1,000)

**Elements:**
1. **Willfully injuring or committing depredation** against property of the United States
2. The target is the Richard B. Russell Federal Building — federal government property
3. Manifesto and surveillance demonstrate willful intent

#### 3. 18 U.S.C. § 115(a)(1) — Threatening Federal Officials

**Severity:** Felony (up to 10 years)

**Elements:**
1. **Threatening to assault, kidnap, or murder** — The manifesto detailed plans to attack the courthouse
2. **A United States judge, federal law enforcement officer, or official** — Federal courthouse targets federal judges and court personnel
3. **With intent to impede, intimidate, or retaliate** — Manifesto likely articulates grievances against the federal government

**Elements likely satisfied depending on manifesto content.**

#### 4. 18 U.S.C. § 1038 — False Information and Hoaxes / Threats Against Federal Buildings

Note: More applicable statute below.

#### 5. 18 U.S.C. § 930(a)/(b) — Possession of Firearms in Federal Facilities (Planned)

**Severity:** Felony (up to 5 years for possession; up to 17 years with intent to commit a crime)

**Elements:**
1. **Knowingly possessing a firearm** in a federal facility — While not yet carried out, the detailed plan and acquisition of weapons demonstrate intent
2. **Intent to commit a crime of violence** — The manifesto and preparations clearly indicate this intent

**This charge would apply upon attempted entry. Current evidence supports conspiracy/attempt.**

#### 6. 18 U.S.C. § 2385 — Advocating Overthrow of Government

**Severity:** Felony (up to 20 years)

**Application depends on manifesto content** — if it advocates violence against the government as a political act.

#### 7. 18 U.S.C. § 2339A — Providing Material Support for Terrorism

**Severity:** Felony (up to 15 years; life if death results)

**Elements:**
1. **Providing material support or resources** — The overseas contact provided "encouragement and tactical advice"
2. **Knowing or intending that they are to be used in preparation for or in carrying out** a federal crime of terrorism

**This applies to the overseas contact, and potentially to the subject if he provided information back.**

#### 8. 18 U.S.C. § 2339B — Providing Material Support to Foreign Terrorist Organizations

**Severity:** Felony (up to 20 years; life if death results)

**If the overseas individual is affiliated with a designated FTO**, both parties face charges under this statute.

#### 9. 18 U.S.C. § 373 — Solicitation to Commit a Crime of Violence

**Severity:** Felony (up to half the maximum for the underlying offense, or life if the underlying offense is punishable by life)

**If the overseas contact solicited or encouraged the attack**, this applies to them. If the subject solicited tactical advice, it may apply to him.

#### 10. 18 U.S.C. § 2332b(a)(1) — Acts of Terrorism Transcending National Boundaries

**Severity:** Felony (up to life imprisonment)

**Elements:**
1. **Conduct transcending national boundaries** — Communication with overseas individual for tactical advice
2. **Involving violent acts dangerous to human life** — Planned armed attack on courthouse
3. **That violate federal or state criminal law** — Multiple violations identified

**All elements likely satisfied given the international communication component.**

#### 11. 18 U.S.C. § 371 — Conspiracy

**Severity:** Felony (up to 5 years, or maximum of underlying offense)

**Elements:**
1. **Agreement between two or more persons** — Subject and overseas contact communicated about the attack
2. **To commit a federal offense** — Planning attack on federal building
3. **Overt act** — Purchasing weapons, conducting surveillance, creating maps

**All elements satisfied.**

#### 12. O.C.G.A. § 16-11-37 — Terroristic Threats (Georgia)

**Severity:** Felony (1 to 5 years)

**Elements:**
1. **Threatening to commit a crime of violence** — The manifesto constitutes a threat
2. **With the purpose of terrorizing another** or causing evacuation of a building

#### 13. O.C.G.A. § 16-4-1 — Criminal Attempt (Georgia)

**Severity:** Felony (up to half the maximum sentence of the intended crime)

**The acquisition of weapons, ammunition, body armor, surveillance, and detailed planning constitute substantial steps toward commission of the crime.**

### Jurisdictional Notes
- **Primary jurisdiction: Federal** — Target is a federal building; terrorism-related offenses; international communications component
- FBI JTTF is lead agency
- **Northern District of Georgia** (Atlanta Division) for federal prosecution
- National Security Division (DOJ) likely involved given terrorism nexus
- Georgia state charges may be pursued concurrently
- FISA warrant may be applicable for the overseas communications

### Immediate Law Enforcement Priorities
1. **Subject in custody** — Determine if the subject should be held without bail as a danger to the community (18 U.S.C. § 3142(f))
2. **Overseas contact investigation** — Identify the foreign individual; determine FTO affiliation; coordinate with international partners
3. **Digital forensics** — Full exploitation of devices, internet history, communications
4. **Determine if others are involved** — Is this a lone actor or part of a broader network?
5. **Assess if other targets exist** — The manifesto and communications may reveal additional planned attacks

### Sentencing Considerations
- Terrorism enhancement under USSG § 3A1.4 dramatically increases sentencing range (minimum Category VI criminal history)
- Multiple consecutive sentences likely
- Life imprisonment possible under several statutes
- Forfeiture of all weapons, equipment, and vehicles used in furtherance
- The suspect's age (22) and lack of prior criminal history may be a mitigating factor, but terrorism enhancements typically override

### Additional Information Needed
- Full content of the manifesto (specific threats, ideology, named targets)
- Identity and affiliation of the overseas contact
- Whether the overseas contact is affiliated with a designated FTO
- Complete digital forensics of all devices
- Financial records (funding sources for weapons and equipment purchases)
- Whether any additional individuals were aware of the plan
- Whether the subject attempted to recruit others
- Behavioral history (mental health, radicalization timeline)

### Summary
This is a **federal domestic terrorism case** with an international nexus. The subject took substantial concrete steps toward carrying out an armed attack on a federal courthouse: manifesto, weapon acquisition, ammunition, body armor, surveillance, building maps, and coordination with an overseas contact. Primary charges include **Conspiracy** (§ 371), **Acts of Terrorism Transcending National Boundaries** (§ 2332b), **Material Support** (§ 2339A/B), **Threatening Federal Officials** (§ 115), and potentially **Attempted Use of WMD** (§ 2332a) if explosive components are found. The terrorism sentencing enhancement under USSG § 3A1.4 ensures the maximum possible sentence. Immediate priorities are securing the subject in custody, identifying the overseas contact, and determining if this is part of a broader network or a lone-actor case."""}
        ],
        "type": "incident_analysis",
        "jurisdiction": "both",
        "statutes_referenced": ["18 U.S.C. § 2332a", "18 U.S.C. § 1361", "18 U.S.C. § 115(a)(1)", "18 U.S.C. § 930", "18 U.S.C. § 2385", "18 U.S.C. § 2339A", "18 U.S.C. § 2339B", "18 U.S.C. § 373", "18 U.S.C. § 2332b(a)(1)", "18 U.S.C. § 371", "O.C.G.A. § 16-11-37", "O.C.G.A. § 16-4-1"],
    },

    # === GEORGIA: DUI / VEHICULAR HOMICIDE ===
    {
        "messages": [
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": """Analyze the following incident for potential criminal violations:

At approximately 1:45 AM, a 28-year-old male driving a pickup truck ran a red light at the intersection of Ponce de Leon Avenue and North Highland Avenue in Atlanta, Georgia, striking a sedan in the driver's side. The driver of the sedan, a 35-year-old female, was pronounced dead at Grady Memorial Hospital. The passenger in the sedan sustained a broken femur and fractured ribs. The pickup driver showed signs of intoxication: slurred speech, bloodshot eyes, odor of alcohol. Field sobriety tests indicated impairment. A breathalyzer test administered at the scene showed a BAC of 0.14. The suspect's driving record shows a prior DUI conviction from 2023. He was also driving with a suspended license (suspended due to the prior DUI). An open container of whiskey was found in the vehicle. Speed was estimated at 55 MPH in a 35 MPH zone."""},
            {"role": "assistant", "content": """## Criminal Law Analysis

### Potential Violations Identified

#### 1. O.C.G.A. § 40-6-393(a) — Vehicular Homicide in the First Degree

**Severity:** Felony (3 to 15 years imprisonment)

**Elements of the Offense:**
1. **Causing the death of another person** — The sedan driver was pronounced dead at Grady Memorial Hospital
2. **Without malice aforethought** — No evidence of intentional killing
3. **By violation of O.C.G.A. § 40-6-391 (DUI)** — BAC of 0.14 (well above 0.08 legal limit), failed field sobriety tests, signs of intoxication

**All elements satisfied. First degree vehicular homicide applies because the underlying offense is DUI.**

#### 2. O.C.G.A. § 40-6-391(a) — Driving Under the Influence (DUI)

**Severity:** Misdemeanor for first offense; **High and Aggravated Misdemeanor** for second offense (this is the suspect's second DUI)

Second offense penalties (within 10 years of prior):
- Mandatory minimum 72 hours jail (up to 12 months)
- $600–$1,000 fine
- 240 hours community service
- Mandatory clinical evaluation
- 18-month license suspension (minimum)
- Ignition interlock device

**Elements:**
1. **Driving or being in actual physical control of a moving vehicle** — Suspect was driving the pickup truck
2. **Under the influence of alcohol to the extent it was less safe to drive** — BAC 0.14, failed FSTs, signs of intoxication
3. **BAC of 0.08 or more** — 0.14 confirmed by breathalyzer

**All elements satisfied. This is a SECOND DUI offense.**

#### 3. O.C.G.A. § 40-6-393.1 — Serious Injury by Vehicle

**Severity:** Felony (1 to 15 years)

**Elements:**
1. **Causing bodily harm to another** — Passenger sustained broken femur and fractured ribs
2. **By violation of DUI statute** — BAC of 0.14
3. **Resulting in serious injury** — Broken femur and fractured ribs constitute serious injury

**All elements satisfied for the injured passenger.**

#### 4. O.C.G.A. § 40-5-121(a) — Driving While License Suspended

**Severity:** Misdemeanor (minimum 2 days jail, up to 12 months; $500–$1,000 fine)

**Elements:**
1. **Operating a motor vehicle** on public roads
2. **While license is suspended** — License was suspended due to prior DUI

**All elements satisfied.**

#### 5. O.C.G.A. § 40-6-253 — Failure to Obey Traffic Control Device (Running Red Light)

**Severity:** Misdemeanor (fine and points)

**Elements:**
1. **Failing to obey a traffic control device** — Ran a red light at the intersection

**Satisfied. This is also the proximate cause of the collision.**

#### 6. O.C.G.A. § 40-6-181 — Speeding

**Severity:** Misdemeanor

**Elements:**
1. **Exceeding the posted speed limit** — Traveling 55 MPH in a 35 MPH zone (20 MPH over)

**Satisfied. Excessive speed is an aggravating factor in the fatality.**

#### 7. O.C.G.A. § 40-6-253.1 / § 40-6-391(d) — Open Container Violation

**Severity:** Misdemeanor ($200 fine)

**Elements:**
1. **Open alcoholic beverage container** within the passenger area of a motor vehicle — Open container of whiskey found in vehicle

**Satisfied.**

#### 8. O.C.G.A. § 40-6-393(b) — Vehicular Homicide in the Second Degree (Alternative)

**Severity:** Misdemeanor (up to 12 months, $1,000 fine)

**Note:** Second degree vehicular homicide applies when death is caused by violation of traffic laws OTHER than DUI. Here, both the speeding and red light violation independently caused the death. However, first degree (DUI-based) is the primary charge and carries greater penalties.

#### 9. O.C.G.A. § 16-5-21 — Aggravated Assault (Potential)

**Severity:** Felony (1 to 20 years)

**Application:** Some prosecutors may charge aggravated assault for the surviving passenger's serious injuries, arguing that driving at 0.14 BAC at 55 MPH through a red light constitutes reckless conduct with a "deadly weapon" (the vehicle). This is a more aggressive charging theory but has been used in Georgia.

### Jurisdictional Notes
- **Georgia state jurisdiction** — City of Atlanta, Fulton County
- Primary: Atlanta Police Department
- Venue: Fulton County Superior Court (felonies), State Court (misdemeanors)
- No federal nexus
- GBI may assist with accident reconstruction

### Sentencing Considerations
- **Prior DUI conviction (2023)** is a significant aggravating factor
- Driving on a suspended license shows willful disregard for court orders
- BAC of 0.14 is nearly double the legal limit
- Speeding 20 MPH over the limit in addition to DUI shows extreme recklessness
- Open container shows the suspect was actively drinking while driving
- Georgia mandatory minimum for vehicular homicide first degree: 3 years
- **Consecutive sentences** likely for vehicular homicide + serious injury by vehicle
- License revocation (permanent or long-term)
- **Habitual violator** designation under O.C.G.A. § 40-5-58 if three or more qualifying offenses

### Additional Information Needed
- Official toxicology report (blood draw at hospital — more accurate than breathalyzer)
- Whether any drugs were also in the suspect's system (enhances DUI charge)
- Accident reconstruction report confirming speed estimate
- Whether the suspect has any additional prior traffic offenses
- Victim impact statements from the deceased's family and injured passenger
- Whether the suspect was on probation from the 2023 DUI (probation violation)
- Dashboard camera or body camera footage
- Exact date of 2023 DUI conviction (must be within 10 years for second offense enhancement)

### Summary
This is a devastating DUI case resulting in death. The primary charges are **Vehicular Homicide in the First Degree** (O.C.G.A. § 40-6-393(a), felony, 3–15 years), **Serious Injury by Vehicle** (§ 40-6-393.1, felony, 1–15 years), **DUI Second Offense** (§ 40-6-391), and **Driving on Suspended License** (§ 40-5-121). The combination of a prior DUI, suspended license, 0.14 BAC, 20 MPH over the speed limit, running a red light, and an open container paints a picture of extreme recklessness. The suspect likely faces 5–15+ years imprisonment when sentences are run consecutively. The prior DUI and suspended license demonstrate that the suspect was already on notice that his drinking and driving posed a danger to others."""}
        ],
        "type": "incident_analysis",
        "jurisdiction": "georgia",
        "statutes_referenced": ["O.C.G.A. § 40-6-393(a)", "O.C.G.A. § 40-6-391(a)", "O.C.G.A. § 40-6-393.1", "O.C.G.A. § 40-5-121(a)", "O.C.G.A. § 40-6-253", "O.C.G.A. § 40-6-181", "O.C.G.A. § 40-6-393(b)", "O.C.G.A. § 16-5-21"],
    },

    # === FEDERAL: PUBLIC CORRUPTION ===
    {
        "messages": [
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": """Analyze the following incident for potential criminal violations:

A multi-year FBI investigation revealed that a county commissioner in Bibb County, Georgia accepted approximately $175,000 in cash payments and gifts (including a vacation home renovation valued at $45,000) from a construction company owner in exchange for steering county contracts worth $3.2 million to that company. The commissioner voted in favor of awarding the contracts at public meetings without disclosing the financial relationship. The construction company submitted inflated invoices, and the commissioner approved payments knowing they were fraudulent. Recorded conversations captured the commissioner discussing future payments and the need to "keep things quiet." The commissioner also filed false financial disclosure statements omitting the payments."""},
            {"role": "assistant", "content": """## Criminal Law Analysis

### Potential Violations Identified

#### 1. 18 U.S.C. § 666(a)(1)(B) — Theft or Bribery Concerning Programs Receiving Federal Funds

**Severity:** Felony (up to 10 years, $250,000 fine)

**Elements of the Offense:**
1. **Agent of a state or local government** — County commissioner is an agent of Bibb County government
2. **Government entity receives more than $10,000 in federal funds annually** — Virtually all Georgia counties receive federal funds exceeding this threshold
3. **Corruptly solicits, demands, accepts, or agrees to accept anything of value** — $175,000 in cash plus $45,000 renovation ($220,000 total)
4. **Intending to be influenced or rewarded in connection with any business or transaction** — Commissioner steered $3.2M in county contracts to the construction company

**All elements satisfied. This is the primary federal bribery statute for local officials.**

#### 2. 18 U.S.C. § 1951 — Hobbs Act Extortion/Bribery

**Severity:** Felony (up to 20 years)

**Elements:**
1. **Obtaining property from another** — Commissioner obtained $220,000 in payments and benefits
2. **Under color of official right** — Using his position as county commissioner to influence contract awards
3. **Affecting interstate commerce** — Construction contracts affect interstate commerce (materials, equipment, labor)

**All elements satisfied. The Hobbs Act is commonly used for public corruption prosecuting bribery "under color of official right."**

#### 3. 18 U.S.C. § 1341 — Mail Fraud

**Severity:** Felony (up to 20 years)

**Elements:**
1. **Scheme to defraud** — The scheme to steer contracts in exchange for bribes, and approval of inflated invoices
2. **Use of the U.S. mails** — County government business routinely involves mail (contracts, invoices, payments, financial disclosures)
3. **Intent to defraud** — Recorded conversations about "keeping things quiet" demonstrate intent

**Elements likely satisfied — mail use is virtually certain in county contracting.**

#### 4. 18 U.S.C. § 1343 — Wire Fraud

**Severity:** Felony (up to 20 years)

**Elements:**
1. **Scheme to defraud** — Same scheme as above
2. **Use of interstate wire communications** — Electronic payments, emails, electronic filing of invoices
3. **Intent to defraud** — Demonstrated by concealment and recorded statements

**All elements likely satisfied.**

#### 5. 18 U.S.C. § 1346 — Honest Services Fraud

**Severity:** Felony (prosecuted under § 1341/1343, up to 20 years)

**Elements:**
1. **Scheme to deprive another of the intangible right of honest services** — The citizens of Bibb County were deprived of their commissioner's honest and faithful service
2. **Through bribery or kickbacks** — $220,000 in bribes in exchange for official acts

**All elements satisfied. This is the "honest services" theory of mail/wire fraud.**

#### 6. 18 U.S.C. § 1001 — False Statements

**Severity:** Felony (up to 5 years)

**Elements:**
1. **Knowingly and willfully making false statements** — Filing false financial disclosure statements
2. **In a matter within the jurisdiction of the federal government** — If the disclosures are filed with or affect federal programs or investigations

**Elements likely satisfied if the disclosure forms have any federal nexus.**

#### 7. 18 U.S.C. § 371 — Conspiracy

**Severity:** Felony (up to 5 years)

**Elements:**
1. **Agreement** — Commissioner and construction company owner agreed to the bribery scheme
2. **To commit a federal offense** — Bribery, fraud, false statements
3. **Overt act** — Payments, votes, contract awards, inflated invoices

**All elements satisfied. Both the commissioner and the construction company owner are co-conspirators.**

#### 8. 26 U.S.C. § 7201 — Tax Evasion

**Severity:** Felony (up to 5 years, $250,000 fine)

**Elements:**
1. **Willfully attempting to evade or defeat a tax** — The $220,000 in bribe income was almost certainly not reported on tax returns
2. **Affirmative act of evasion** — Failing to report income; filing false financial disclosures

**Elements likely satisfied — unreported bribe income is taxable.**

#### 9. O.C.G.A. § 16-10-2 — Bribe Taking by Public Official (Georgia)

**Severity:** Felony (1 to 20 years)

**Elements:**
1. **Public officer** — County commissioner
2. **Accepts or agrees to accept anything of value** — $220,000 in payments and benefits
3. **For performing or failing to perform official duties** — Voting to award contracts

**All elements satisfied under Georgia state law.**

#### 10. O.C.G.A. § 16-10-1 — Influencing a Public Official (Bribery) — Against the Construction Company Owner

**Severity:** Felony (1 to 5 years)

**Elements:**
1. **Giving or offering anything of value** — $220,000 to the commissioner
2. **To influence the official's actions** — To secure $3.2M in county contracts

**All elements satisfied against the construction company owner.**

### Charges Against the Construction Company Owner

The construction company owner faces:
- 18 U.S.C. § 666(a)(2) — Offering bribes to local government agent
- 18 U.S.C. § 1951 — Hobbs Act (paying bribes)
- 18 U.S.C. § 1341/1343 — Mail/Wire Fraud
- 18 U.S.C. § 371 — Conspiracy
- O.C.G.A. § 16-10-1 — Bribery of public official
- Potential fraud charges for submitting inflated invoices to the county

### Jurisdictional Notes
- **Primary jurisdiction: Federal** — FBI investigation, federal funding nexus, Hobbs Act
- Middle District of Georgia (Macon Division) for federal prosecution
- Bibb County for state charges
- Federal prosecution typically takes priority in public corruption cases
- The recorded conversations provide strong direct evidence

### Sentencing Considerations
- Federal Sentencing Guidelines: offense level driven by bribe amount ($220K) and loss to government (inflated invoices on $3.2M in contracts)
- Abuse of trust enhancement (USSG § 3B1.3)
- Public official enhancement
- Forfeiture of bribe proceeds ($220K) under 18 U.S.C. § 981
- Restitution to Bibb County for overpayments on inflated invoices
- Possible RICO charges (18 U.S.C. § 1962) if the pattern is sufficiently extensive

### Additional Information Needed
- Total amount of inflated invoicing (loss amount for sentencing)
- Whether other county officials were involved (broader conspiracy)
- Federal funding received by Bibb County (confirms § 666 jurisdiction)
- Tax returns for both subjects (unreported income)
- Full scope of recorded conversations
- Whether the construction company performed substandard work (public safety issue)
- Duration and full extent of the corrupt relationship

### Summary
This is a comprehensive **federal public corruption case**. The commissioner faces charges under the **Hobbs Act** (§ 1951, 20 years), **Federal Program Bribery** (§ 666, 10 years), **Mail/Wire Fraud** including **Honest Services Fraud** (§ 1341/1343/1346, 20 years), **Conspiracy** (§ 371), **False Statements** (§ 1001), and likely **Tax Evasion** (§ 7201). The construction company owner faces parallel bribery and fraud charges. Recorded conversations provide devastating direct evidence. Federal Sentencing Guidelines calculations based on $220K in bribes and potentially millions in fraudulent invoices will result in a significant prison sentence. Georgia state bribery charges may be pursued concurrently or held in reserve."""}
        ],
        "type": "incident_analysis",
        "jurisdiction": "both",
        "statutes_referenced": ["18 U.S.C. § 666", "18 U.S.C. § 1951", "18 U.S.C. § 1341", "18 U.S.C. § 1343", "18 U.S.C. § 1346", "18 U.S.C. § 1001", "18 U.S.C. § 371", "26 U.S.C. § 7201", "O.C.G.A. § 16-10-2", "O.C.G.A. § 16-10-1"],
    },

    # === GEORGIA: ARMED ROBBERY / CARJACKING ===
    {
        "messages": [
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": """Analyze the following incident for potential criminal violations:

At approximately 9:30 PM in a parking garage in Buckhead, Atlanta, Georgia, a victim was approached by two suspects as she was getting into her car. Suspect 1 displayed a knife and demanded her car keys, purse, and cell phone. When the victim hesitated, Suspect 2 grabbed her arm and shoved her to the ground, causing scrapes and bruises. They took her 2024 Mercedes-Benz (valued at $62,000), her purse containing $400 cash, credit cards, and her iPhone. The suspects were captured on parking garage cameras. They were later identified when they used the victim's credit card at a gas station 30 minutes later. The vehicle was recovered the next day. The victim also reported that Suspect 1 said "Don't call the cops or we'll find you" before fleeing."""},
            {"role": "assistant", "content": """## Criminal Law Analysis

### Potential Violations Identified

#### 1. O.C.G.A. § 16-8-41(a) — Armed Robbery

**Severity:** Felony (10 to 20 years mandatory, no parole for minimum)

**Elements of the Offense:**
1. **Taking property of another from the person or immediate presence** — Car keys, purse, cash, phone, and vehicle taken directly from the victim
2. **With intent to commit theft** — Suspects intended to permanently deprive the victim of her property
3. **By use of an offensive weapon** — Suspect 1 displayed a knife (an offensive weapon)

**All elements satisfied. Armed robbery carries a 10-year mandatory minimum in Georgia with no possibility of parole during that period.**

#### 2. O.C.G.A. § 16-5-21(a)(1) — Aggravated Assault

**Severity:** Felony (1 to 20 years)

**Elements:**
1. **Assault with intent to rob** — The knife display and demands constitute an assault with intent to rob
2. **With a deadly weapon** — A knife is a deadly weapon under Georgia law

**Elements satisfied. This may merge with armed robbery for sentencing purposes.**

#### 3. O.C.G.A. § 16-5-21(a)(2) — Aggravated Assault (Against Victim)

**Severity:** Felony (1 to 20 years)

**Elements:**
1. **Assault with a deadly weapon or object likely to cause serious bodily injury** — Knife
2. **Against the victim** — Threatening the victim with the knife

**Satisfied as an alternative theory.**

#### 4. O.C.G.A. § 16-5-24(b) — Aggravated Battery

**Severity:** Felony (1 to 20 years)

**Note:** The shoving causing scrapes and bruises may not rise to "serious disfigurement" or "rendering a member useless." Simple battery (§ 16-5-23) is more appropriate for the physical contact.

#### 5. O.C.G.A. § 16-5-23(a) — Simple Battery

**Severity:** Misdemeanor (up to 12 months)

**Elements:**
1. **Intentionally making physical contact of an insulting or provoking nature** — Grabbing victim's arm and shoving her to the ground
2. **Or intentionally causing physical harm** — Scrapes and bruises from the fall

**Satisfied for Suspect 2 who physically assaulted the victim.**

#### 6. O.C.G.A. § 16-8-2 — Theft by Taking (Felony)

**Severity:** Felony (1 to 20 years for property valued over $25,000)

**Elements:**
1. **Unlawfully taking property of another** — Mercedes ($62,000), purse, cash ($400), phone
2. **With intent to deprive** — Property taken and used/kept
3. **Total value exceeds $25,000** — Vehicle alone is $62,000

**Satisfied. The felony threshold for over $25,000 applies (O.C.G.A. § 16-8-12).**

#### 7. O.C.G.A. § 16-8-9 — Financial Transaction Card Theft

**Severity:** Felony (1 to 3 years for first offense; 3 to 5 years for subsequent)

**Elements:**
1. **Taking a financial transaction card from the person or possession of another** — Credit cards taken from victim's purse

**Satisfied.**

#### 8. O.C.G.A. § 16-8-17 — Financial Transaction Card Fraud

**Severity:** Felony (1 to 5 years)

**Elements:**
1. **Using a financial transaction card** obtained unlawfully
2. **To obtain goods or services** — Used at a gas station 30 minutes after the robbery
3. **Knowing the use is unauthorized** — Cards were just stolen

**All elements satisfied for the gas station purchase.**

#### 9. O.C.G.A. § 16-10-7 — Influencing Witnesses / Intimidation of Victim

**Severity:** Felony (1 to 5 years)

**Elements:**
1. **Threatening or intimidating a victim or witness** — "Don't call the cops or we'll find you"
2. **With intent to deter reporting** — Explicit statement to not call police

**Satisfied. The threat to the victim constitutes witness/victim intimidation.**

#### 10. 18 U.S.C. § 2119 — Federal Carjacking

**Severity:** Felony (up to 15 years; up to 25 years if serious bodily injury)

**Elements:**
1. **Taking a motor vehicle from the person or presence of another** — Vehicle taken directly from the victim
2. **By force and violence or by intimidation** — Knife, physical assault, threats
3. **With intent to cause death or serious bodily harm** — Display of knife demonstrates at least conditional intent

**Note: Federal carjacking requires that the vehicle was "transported, shipped, or received in interstate or foreign commerce." A 2024 Mercedes-Benz was certainly manufactured and shipped in interstate commerce. Federal prosecution is possible but state charges may be preferred given the strong Georgia statutes.**

### Jurisdictional Notes
- **Primary jurisdiction: Georgia state** — Fulton County (Buckhead is in Atlanta)
- Atlanta Police Department, Zone 2
- Venue: Fulton County Superior Court
- Federal carjacking charges (18 U.S.C. § 2119) are available but state charges carry equally strong penalties
- If the stolen vehicle crossed state lines, federal charges become more likely

### Sentencing Considerations
- **Armed robbery: 10-year mandatory minimum** — No parole, no early release during this period
- Repeat offender status would increase penalties
- Multiple victims of theft (credit card company also victimized)
- Aggravating factors: nighttime, parking garage (vulnerability), weapon, threats, physical violence
- Each suspect liable for all offenses under party to a crime theory (O.C.G.A. § 16-2-20)
- Credit card fraud adds additional consecutive felony counts

### Additional Information Needed
- Identification of both suspects from parking garage footage
- Prior criminal records of both suspects (affects sentencing dramatically)
- Forensic evidence from the recovered vehicle (DNA, fingerprints)
- Gas station surveillance footage for identification
- Whether the credit card was used at any other locations
- Whether the stolen iPhone's location services can track suspect movements
- Victim's medical records for injuries (scrapes and bruises documentation)
- Whether the knife was recovered

### Summary
The primary charge is **Armed Robbery** (O.C.G.A. § 16-8-41, felony, **10–20 years mandatory minimum with no parole**). Supporting charges include **Aggravated Assault** (§ 16-5-21), **Felony Theft by Taking** (§ 16-8-2, value over $25,000), **Financial Transaction Card Theft and Fraud** (§§ 16-8-9, 16-8-17), and **Victim Intimidation** (§ 16-10-7). Both suspects are equally liable under Georgia's party to a crime statute. The 10-year mandatory minimum for armed robbery alone, combined with consecutive sentences for the other felonies, means both suspects face 15–30+ years. The gas station credit card use 30 minutes later provides critical identification evidence."""}
        ],
        "type": "incident_analysis",
        "jurisdiction": "both",
        "statutes_referenced": ["O.C.G.A. § 16-8-41(a)", "O.C.G.A. § 16-5-21(a)", "O.C.G.A. § 16-5-23(a)", "O.C.G.A. § 16-8-2", "O.C.G.A. § 16-8-9", "O.C.G.A. § 16-8-17", "O.C.G.A. § 16-10-7", "18 U.S.C. § 2119"],
    },

    # === FEDERAL: CHILD EXPLOITATION ===
    {
        "messages": [
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": """Analyze the following incident for potential criminal violations:

An investigation by the GBI Internet Crimes Against Children (ICAC) task force and the FBI identified a 40-year-old male in Columbus, Georgia who was distributing child sexual abuse material (CSAM) through an encrypted messaging platform. A search warrant executed on his residence recovered three computers and multiple external hard drives containing over 15,000 images and 500 videos of CSAM, including material depicting minors under the age of 12. Digital forensic analysis revealed he had been sharing material with at least 30 other users across multiple countries over a two-year period. Additionally, investigators found evidence he had used a social media platform to communicate with a 13-year-old victim, sending sexually explicit messages and requesting nude photographs, which the victim provided under coercion. He had planned to meet the victim in person."""},
            {"role": "assistant", "content": """## Criminal Law Analysis

### Potential Violations Identified

#### 1. 18 U.S.C. § 2252(a)(2) — Distribution of Child Sexual Abuse Material

**Severity:** Felony (5 to 20 years mandatory; 15 to 40 years if prior sex offense conviction)

**Elements of the Offense:**
1. **Knowingly distributing** — Sharing material with 30+ users over two years
2. **Visual depictions involving minors engaged in sexually explicit conduct** — 15,000+ images and 500 videos of CSAM
3. **Using any means of interstate or foreign commerce** — Encrypted messaging platform (internet)
4. **Knowing that the material depicts minors** — Volume and duration indicate knowledge

**All elements satisfied. Distribution carries higher penalties than possession.**

#### 2. 18 U.S.C. § 2252(a)(4)(B) — Possession of Child Sexual Abuse Material

**Severity:** Felony (up to 10 years for first offense; up to 20 years if prior sex offense)

**Elements:**
1. **Knowingly possessing** — Material on computers and external hard drives in his residence
2. **Visual depictions of minors engaged in sexually explicit conduct** — 15,000+ images, 500 videos
3. **That were produced using materials shipped in interstate commerce** — Computers, hard drives, internet

**All elements satisfied.**

#### 3. 18 U.S.C. § 2251(a) — Sexual Exploitation of Children (Production)

**Severity:** Felony (15 to 30 years mandatory minimum; 25 to 50 years if prior conviction)

**Elements:**
1. **Employing, using, persuading, inducing, enticing, or coercing a minor** — Coerced a 13-year-old victim to send nude photographs
2. **To engage in sexually explicit conduct** — Nude photographs constitute sexually explicit conduct
3. **For the purpose of producing visual depictions** — Requested and received photographs
4. **Using interstate commerce** — Social media platform, internet communications

**All elements satisfied. Production carries the highest penalties — 15-year mandatory minimum.**

#### 4. 18 U.S.C. § 2422(b) — Enticement of a Minor

**Severity:** Felony (10 years to life imprisonment)

**Elements:**
1. **Using a facility of interstate commerce** — Social media platform
2. **To knowingly persuade, induce, entice, or coerce** — Sending explicit messages, requesting photographs
3. **Any individual under 18 years of age** — Victim is 13 years old
4. **To engage in sexual activity** — Requesting nude photographs constitutes sexual activity for purposes of this statute

**All elements satisfied. Mandatory minimum of 10 years.**

#### 5. 18 U.S.C. § 2423(b) — Travel with Intent to Engage in Illicit Sexual Conduct (Attempted)

**Severity:** Felony (up to 30 years)

**Elements:**
1. **Traveling in interstate commerce** — Planning to meet the victim
2. **For the purpose of engaging in illicit sexual conduct** with a minor

**If the planned meeting involved any travel across state lines, this charge applies. Even within Georgia, attempted travel may be charged.**

#### 6. 18 U.S.C. § 2252A(a)(1) — Distribution of Material Constituting Child Pornography

**Severity:** Felony (5 to 20 years)

**Alternative/additional to § 2252 — may be charged for material that meets additional definitional criteria.**

#### 7. 18 U.S.C. § 2260 — Production of Sexually Explicit Depictions of a Minor for Importation

**Severity:** Felony (15 to 30 years)

**If any of the material shared with international users was produced by the suspect, this applies.**

#### 8. 18 U.S.C. § 371 — Conspiracy

**Severity:** Felony (up to 5 years)

**The two-year sharing network with 30+ users across multiple countries constitutes a conspiracy to distribute CSAM.**

#### 9. O.C.G.A. § 16-12-100(b)(8) — Sexual Exploitation of Children (Georgia)

**Severity:** Felony (5 to 20 years per image/video for first offense; 10 to 30 years for subsequent)

**Elements:**
1. **Possessing or distributing** material depicting a minor engaged in sexually explicit conduct
2. **15,000 images + 500 videos** = potentially 15,500 separate counts

**Georgia penalties stack PER IMAGE/VIDEO. This creates extraordinary exposure.**

#### 10. O.C.G.A. § 16-12-100.2(d) — Computer Pornography and Child Exploitation Prevention

**Severity:** Felony (1 to 20 years)

**Elements:**
1. **Using a computer** to seduce, solicit, lure, or entice a child to commit sexual acts
2. Communications with the 13-year-old victim via social media

**All elements satisfied.**

#### 11. O.C.G.A. § 16-6-8 — Enticing a Child for Indecent Purposes

**Severity:** Felony (10 to 30 years)

**Elements:**
1. **Soliciting, enticing, or taking a person under 16** for indecent purposes
2. Coercing the 13-year-old to send nude photographs

**All elements satisfied.**

### Jurisdictional Notes
- **Primary jurisdiction: Federal** — Interstate and international distribution via internet establishes clear federal jurisdiction
- FBI and GBI ICAC task force joint investigation
- **Middle District of Georgia** (Columbus Division)
- Federal prosecution preferred due to: higher mandatory minimums, international scope, established federal frameworks for CSAM cases
- Georgia state charges provide additional leverage and can be held in reserve
- **International cooperation** needed for the 30+ overseas recipients via MLAT (Mutual Legal Assistance Treaty)
- NCMEC (National Center for Missing & Exploited Children) involvement for victim identification

### Victim Protection
- The 13-year-old victim needs immediate forensic interview (per ICAC protocols)
- Victim advocacy services under the Crime Victims' Rights Act (18 U.S.C. § 3771)
- Consider whether the distributed material includes identified victims who need notification
- Determine if additional minors were contacted

### Sentencing Considerations
- **Production (§ 2251): 15-year mandatory minimum** — this alone ensures substantial prison time
- **Enticement (§ 2422(b)): 10-year mandatory minimum**
- **Distribution (§ 2252): 5-year mandatory minimum**
- Federal sentences run CONSECUTIVELY for distinct victims/counts
- USSG § 2G2.1/2G2.2 enhancements for:
  - Number of images (15,000+): significant upward adjustment
  - Age of victims (under 12): +2 levels
  - Distribution to others: +2 levels
  - Use of computer: +2 levels
  - Pattern of activity: +5 levels
- Likely **effective life sentence** given the volume, distribution scope, and production charge
- Mandatory sex offender registration under SORNA
- Supervised release conditions will be extensive and lifelong

### Additional Information Needed
- Full forensic analysis of all devices
- Identification of all 30+ recipients (potential co-defendants)
- Analysis of encrypted communications for additional victims
- Whether any hands-on abuse occurred (either with the 13-year-old or others)
- Whether any of the 15,000+ images were self-produced by the suspect
- Victim identification analysis through NCMEC
- Financial records (possible commercial distribution)
- Whether the encrypted platform has cooperated with law enforcement

### Summary
This is an extremely serious federal child exploitation case involving **production, distribution, and possession of CSAM** combined with **online enticement and coercion of a 13-year-old victim**. The mandatory minimums alone total **30+ years** (15 for production + 10 for enticement + 5 for distribution). With 15,000+ images, 500 videos, distribution to 30+ international users over two years, and direct victimization of a minor, the Federal Sentencing Guidelines will almost certainly produce an **effective life sentence**. This case requires coordination between FBI, GBI ICAC, NCMEC, and international law enforcement partners to identify all victims and co-conspirators."""}
        ],
        "type": "incident_analysis",
        "jurisdiction": "both",
        "statutes_referenced": ["18 U.S.C. § 2252(a)(2)", "18 U.S.C. § 2252(a)(4)(B)", "18 U.S.C. § 2251(a)", "18 U.S.C. § 2422(b)", "18 U.S.C. § 2423(b)", "18 U.S.C. § 2252A(a)(1)", "18 U.S.C. § 371", "O.C.G.A. § 16-12-100(b)(8)", "O.C.G.A. § 16-12-100.2(d)", "O.C.G.A. § 16-6-8"],
    },

    # === FEDERAL: ENVIRONMENTAL CRIME ===
    {
        "messages": [
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": """Analyze the following incident for potential criminal violations:

EPA investigators discovered that a chemical manufacturing company in Augusta, Georgia had been illegally dumping industrial waste containing heavy metals (lead, mercury, and cadmium) into a tributary of the Savannah River for approximately 18 months. Testing revealed contamination levels 50 times above EPA limits. The company's environmental compliance officer had falsified monthly discharge monitoring reports submitted to the EPA, showing pollutant levels within permitted limits. Internal emails revealed the CEO and plant manager were aware of the illegal dumping and directed it to avoid $2 million in proper waste disposal costs. Three employees who raised concerns were terminated. Downstream municipal water supplies were affected, and elevated blood lead levels were detected in 45 children in the affected communities."""},
            {"role": "assistant", "content": """## Criminal Law Analysis

### Potential Violations Identified

#### 1. 33 U.S.C. § 1319(c)(2) — Clean Water Act: Knowing Violations

**Severity:** Felony (up to 3 years per day of violation; up to 6 years per day for repeat offenders; $50,000/day fine)

**Elements:**
1. **Knowingly discharging pollutants** — CEO and plant manager directed the dumping
2. **Into waters of the United States** — Tributary of the Savannah River is a navigable water of the U.S.
3. **Without a permit or in violation of permit conditions** — Discharge exceeded limits by 50x; falsified reports
4. **Each day of violation is a separate offense** — 18 months ≈ 540+ separate violations

**All elements satisfied. With 540+ days of knowing violations, the potential sentence is extraordinary.**

#### 2. 33 U.S.C. § 1319(c)(3) — Clean Water Act: Knowing Endangerment

**Severity:** Felony (up to 15 years per violation; $250,000 fine per individual; $1M per organization)

**Elements:**
1. **Knowingly violating the Clean Water Act** — Satisfied as above
2. **Placing another person in imminent danger of death or serious bodily injury** — 45 children with elevated blood lead levels; mercury and cadmium exposure to downstream communities
3. **Knowledge that violations place others at risk** — Internal emails show awareness; contamination levels 50x above limits

**All elements satisfied. Knowing endangerment is the most serious CWA criminal provision.**

#### 3. 42 U.S.C. § 6928(d) — RCRA: Knowing Treatment, Storage, or Disposal Without a Permit

**Severity:** Felony (up to 5 years per violation; $50,000/day fine)

**Elements:**
1. **Knowingly treating, storing, or disposing of hazardous waste** — Lead, mercury, and cadmium are hazardous wastes
2. **Without a permit** — Dumping into a waterway is not a permitted disposal method
3. **Or in knowing violation of permit conditions** — Exceeding limits by 50x

**All elements satisfied.**

#### 4. 42 U.S.C. § 6928(e) — RCRA: Knowing Endangerment

**Severity:** Felony (up to 15 years; $250,000 fine per individual; $1M per organization)

**Elements:**
1. **Knowingly violating RCRA** — Satisfied as above
2. **Placing another person in imminent danger of death or serious bodily injury** — Children with elevated blood lead levels

**All elements satisfied.**

#### 5. 18 U.S.C. § 1001 — False Statements to Federal Agency

**Severity:** Felony (up to 5 years per false statement)

**Elements:**
1. **Knowingly and willfully making false statements** — Environmental compliance officer falsified monthly discharge monitoring reports
2. **In a matter within jurisdiction of federal agency** — EPA-required reports
3. **Materially false** — Reported compliant levels when actual levels were 50x over

**All elements satisfied. Each falsified monthly report is a separate count — 18 months = 18 counts.**

#### 6. 33 U.S.C. § 1319(c)(4) — Clean Water Act: False Statements

**Severity:** Felony (up to 2 years; up to 4 years for repeat offenders; $10,000/day fine)

**Elements:**
1. **Knowingly making false statements** in records, reports, or documents submitted under the CWA
2. Monthly discharge monitoring reports were falsified

**All elements satisfied — specific CWA false statement provision.**

#### 7. 18 U.S.C. § 371 — Conspiracy

**Severity:** Felony (up to 5 years)

**Elements:**
1. **Agreement** — CEO, plant manager, and compliance officer conspired
2. **To commit federal offenses** — CWA violations, RCRA violations, false statements
3. **Overt acts** — Directing dumping, falsifying reports, terminating whistleblowers

**All elements satisfied.**

#### 8. 18 U.S.C. § 1512(b) — Obstruction: Witness Tampering / Retaliation

**Severity:** Felony (up to 20 years)

**Elements:**
1. **Knowingly engaging in intimidation, threats, or corrupt persuasion** — OR
2. **Retaliating against a person for providing information to law enforcement** — Three employees terminated for raising concerns
3. Terminating whistleblowing employees constitutes retaliation

**Elements satisfied if the terminated employees raised concerns internally or to regulators.**

#### 9. 18 U.S.C. § 1341/1343 — Mail/Wire Fraud

**Severity:** Felony (up to 20 years)

**Elements:**
1. **Scheme to defraud** — Avoiding $2M in disposal costs through illegal dumping while submitting false compliance reports
2. **Use of mail/wire** — Submission of reports, communications with EPA

**Potentially satisfied — the scheme to avoid costs while appearing compliant constitutes fraud.**

#### 10. O.C.G.A. § 12-5-52 — Georgia Water Quality Control Act Violations

**Severity:** Felony (up to 3 years, $50,000/day fine per individual; $100,000/day per entity)

**Elements:**
1. **Discharging pollutants into waters of the state** without authorization
2. The Savannah River tributary is a water of the state of Georgia

**All elements satisfied under Georgia state law.**

#### 11. O.C.G.A. § 12-8-68 — Georgia Hazardous Waste Management Act

**Severity:** Felony (1 to 5 years per violation)

**Improper disposal of hazardous waste (heavy metals) in violation of Georgia hazardous waste regulations.**

#### 12. O.C.G.A. § 16-5-60(c) — Reckless Conduct (Georgia)

**Severity:** Misdemeanor

**Knowingly causing contamination that resulted in elevated blood lead levels in 45 children constitutes reckless conduct endangering the bodily safety of others.**

### Individual Criminal Liability

**CEO:** Conspiracy, CWA knowing violations, knowing endangerment, RCRA violations, fraud — personally directed the illegal dumping
**Plant Manager:** Same as CEO — directed operations
**Environmental Compliance Officer:** False statements (18 U.S.C. § 1001), CWA false statements, conspiracy — falsified monitoring reports
**Corporate Entity:** Subject to criminal fines under all statutes; potential debarment from government contracts

### Jurisdictional Notes
- **Primary jurisdiction: Federal** — EPA investigation, Clean Water Act, RCRA
- Southern District of Georgia (Augusta Division)
- EPA Criminal Investigation Division (EPA CID) lead agency
- Georgia EPD may pursue parallel state charges
- Civil enforcement (injunctions, cleanup orders) will proceed simultaneously
- Superfund (CERCLA) liability for cleanup costs

### Sentencing Considerations
- **Knowing endangerment** charges carry up to 15 years per violation — with 540+ days, exposure is effectively life imprisonment for responsible individuals
- Each day of illegal discharge is a separate count
- Each falsified report is a separate count
- Federal Sentencing Guidelines: environmental offenses have specific guidelines under USSG § 2Q1.1–2Q1.6
- Enhancement for: ongoing/continuous discharge, vulnerable victims (children), substantial harm to environment
- **Corporate fine** could be tens of millions
- **Restitution** for medical monitoring and treatment of affected communities
- **Cleanup costs** under CERCLA could be tens of millions
- Alternative Fines Act (18 U.S.C. § 3571): fine may be up to twice the gain ($4M+) or twice the loss

### Additional Information Needed
- Full extent of contamination (environmental assessment)
- Complete medical screening of affected communities
- Total number of affected individuals beyond the 45 children identified
- Whether the contamination has reached the Savannah River main stem (multi-state impact — South Carolina)
- Financial records showing cost savings from illegal dumping
- Complete internal email review
- Whether the terminated employees filed complaints with OSHA (potential SOX/environmental whistleblower violations)
- Identity and roles of all employees involved in the dumping operations
- Whether the company has any prior environmental violations

### Summary
This is a major **federal environmental criminal case** involving **knowing endangerment** of public health. The combination of **Clean Water Act** violations (§ 1319(c)(2)/(3)), **RCRA** violations (§ 6928(d)/(e)), **false statements** to the EPA (§ 1001), **conspiracy** (§ 371), and **witness retaliation** (§ 1512) creates enormous criminal exposure. The **knowing endangerment** provisions alone carry up to **15 years per violation** — with 540+ days of illegal dumping, the sentencing exposure for the CEO and plant manager is effectively life imprisonment. The 45 children with elevated blood lead levels provide devastating evidence of actual harm. The company faces criminal fines potentially exceeding $50 million, plus cleanup costs and restitution. Georgia state charges provide additional enforcement leverage."""}
        ],
        "type": "incident_analysis",
        "jurisdiction": "both",
        "statutes_referenced": ["33 U.S.C. § 1319(c)(2)", "33 U.S.C. § 1319(c)(3)", "42 U.S.C. § 6928(d)", "42 U.S.C. § 6928(e)", "18 U.S.C. § 1001", "33 U.S.C. § 1319(c)(4)", "18 U.S.C. § 371", "18 U.S.C. § 1512(b)", "18 U.S.C. § 1341", "O.C.G.A. § 12-5-52", "O.C.G.A. § 12-8-68", "O.C.G.A. § 16-5-60(c)"],
    },
]


def generate_additional_short_examples() -> list[dict]:
    """Generate shorter, focused training examples for common offenses."""
    short_examples = []

    # Quick-reference statute identification examples
    quick_pairs = [
        (
            "A man punched another man in the face at a gas station in Macon, Georgia, breaking his nose.",
            "**O.C.G.A. § 16-5-24(a) — Aggravated Battery** (felony, 1–20 years): Maliciously causing bodily harm by seriously disfiguring the body. A broken nose constitutes serious disfigurement.\n\n**O.C.G.A. § 16-5-23(a) — Battery** (misdemeanor): Intentionally causing physical harm. This is a lesser included offense."
        ),
        (
            "Someone stole a package from a front porch in Atlanta that was delivered by UPS. The package contained electronics worth $500.",
            "**O.C.G.A. § 16-8-2 — Theft by Taking** (misdemeanor for value under $5,000): Unlawfully taking property of another with intent to deprive.\n\n**Note on federal jurisdiction:** If the package was in the stream of interstate commerce (UPS shipment), 18 U.S.C. § 659 (theft from interstate shipment) could apply as a federal charge, though local prosecution is more typical for this value."
        ),
        (
            "A woman forged her employer's signature on three company checks totaling $12,000 and deposited them into her personal bank account.",
            "**O.C.G.A. § 16-9-1(a) — Forgery in the First Degree** (felony, 1–10 years): Making, altering, or possessing a writing (checks) in a fictitious name or with unauthorized alterations, with intent to defraud.\n\n**O.C.G.A. § 16-8-4 — Theft by Conversion** (felony, 1–10 years for $5,000–$25,000): Converting funds entrusted to her by her employer.\n\n**O.C.G.A. § 16-9-31(a) — Deposit Account Fraud** (felony): Depositing forged instruments."
        ),
        (
            "A person was caught growing 120 marijuana plants in their basement in Valdosta, Georgia with grow lights, ventilation, and irrigation systems.",
            "**O.C.G.A. § 16-13-30(j)(2) — Manufacturing Marijuana** (felony, 1–10 years): Growing marijuana plants is manufacturing under Georgia law.\n\n**O.C.G.A. § 16-13-31(c) — Trafficking in Marijuana** (felony, mandatory 5 years, $100,000 fine): 120 plants would likely yield over 10 pounds, meeting the trafficking threshold.\n\n**Note:** Georgia has not legalized recreational marijuana. The sophisticated grow operation (lights, ventilation, irrigation) supports intent to distribute."
        ),
        (
            "A 19-year-old sent unsolicited explicit photographs to a 15-year-old via Instagram in Georgia.",
            "**O.C.G.A. § 16-12-100.1(b) — Electronically Furnishing Obscene Material to Minors** (felony, 1–5 years): Using electronic communication to transmit obscene material to a person known to be under 16.\n\n**O.C.G.A. § 16-12-100.2(d)(1) — Computer or Electronic Pornography and Child Exploitation Prevention** (felony): Using a computer/electronic device to transmit sexually explicit material to a minor."
        ),
        (
            "A person set fire to an abandoned warehouse in Savannah, Georgia at 3 AM. No one was inside.",
            "**O.C.G.A. § 16-7-60(a) — Arson in the First Degree** (felony, 1–20 years): Knowingly damaging or destroying by means of fire or explosive any building of another without consent.\n\n**Note:** Even though the building was abandoned and unoccupied, first degree arson applies to any building/structure. If anyone had been inside, the charge could potentially be elevated and additional charges (reckless endangerment, attempted murder) would apply."
        ),
        (
            "A store manager was caught skimming credit card numbers from customers using a hidden card reader device at a retail store in Cobb County, Georgia.",
            "**O.C.G.A. § 16-9-31(a) — Financial Transaction Card Fraud** (felony, 1–5 years): Using a scanning device to capture card data without authorization.\n\n**O.C.G.A. § 16-8-2 — Theft by Taking** (felony): If funds were withdrawn using the captured data.\n\n**18 U.S.C. § 1029(a)(4) — Access Device Fraud** (federal felony, up to 10 years): Possessing a device to counterfeit access devices. Federal jurisdiction through interstate commerce (credit card networks)."
        ),
        (
            "Police pulled over a driver in DeKalb County, Georgia and discovered he was transporting 30 stolen catalytic converters in his truck bed.",
            "**O.C.G.A. § 16-8-7 — Theft by Receiving Stolen Property** (felony, 1–10 years for value over $5,000): Receiving property knowing it was stolen. 30 catalytic converters are worth $15,000–$45,000.\n\n**O.C.G.A. § 16-8-12(a)(1) — Felony Theft** (1–10 years): Value exceeds $5,000.\n\n**O.C.G.A. § 10-1-360.4 — Unlawful purchase of catalytic converters** (misdemeanor/felony): Georgia has specific statutes regulating catalytic converter sales and purchases enacted to combat this type of theft."
        ),
    ]

    for incident, analysis in quick_pairs:
        short_examples.append({
            "messages": [
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": f"Identify the potential criminal violations in this incident:\n\n{incident}"},
                {"role": "assistant", "content": analysis},
            ],
            "type": "quick_reference",
            "jurisdiction": "georgia",
        })

    return short_examples


def main():
    """Generate and save synthetic training data."""
    print("=" * 60)
    print("SELMA — Generating Synthetic Training Data")
    print("=" * 60)

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    all_examples = []

    # Add detailed incident analyses
    all_examples.extend(SYNTHETIC_EXAMPLES)
    print(f"Detailed incident analyses: {len(SYNTHETIC_EXAMPLES)}")

    # Add short quick-reference examples
    short = generate_additional_short_examples()
    all_examples.extend(short)
    print(f"Quick-reference examples: {len(short)}")

    # Save
    output_path = OUTPUT_DIR / "synthetic_training.jsonl"
    with open(output_path, "w") as f:
        for example in all_examples:
            f.write(json.dumps(example, ensure_ascii=False) + "\n")

    print(f"\nTotal synthetic examples: {len(all_examples)}")
    print(f"Saved to {output_path}")

    # Stats
    stats = {
        "total": len(all_examples),
        "detailed_analyses": len(SYNTHETIC_EXAMPLES),
        "quick_reference": len(short),
        "jurisdictions": {
            "federal": sum(1 for e in all_examples if e.get("jurisdiction") == "federal"),
            "georgia": sum(1 for e in all_examples if e.get("jurisdiction") == "georgia"),
            "both": sum(1 for e in all_examples if e.get("jurisdiction") == "both"),
        },
    }

    stats_path = OUTPUT_DIR / "synthetic_stats.json"
    with open(stats_path, "w") as f:
        json.dump(stats, f, indent=2)

    print(f"\nBreakdown:")
    print(f"  Federal only: {stats['jurisdictions']['federal']}")
    print(f"  Georgia only: {stats['jurisdictions']['georgia']}")
    print(f"  Both: {stats['jurisdictions']['both']}")


if __name__ == "__main__":
    main()
