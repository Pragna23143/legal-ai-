"""Preloaded Sample Legal Agreements for Testing and Demonstrations.

Includes:
1. Enterprise SaaS & Cloud License Agreement (sneaky auto-renewal, indemnification, data rights)
2. Executive Employment & Non-Compete Agreement (severe IP assignment, 2-year non-compete, damages)
3. Commercial Real Estate Lease (triple net pass-through, security deposit forfeiture, late interest)
4. Unilateral Non-Disclosure Agreement (overly broad confidential information, perpetual survival)
"""

from typing import Dict, List

SAMPLE_CONTRACTS: List[Dict[str, str]] = [
    {
        "id": "enterprise-saas",
        "title": "Enterprise Cloud SaaS & Master Subscription Agreement",
        "category": "Technology & Software",
        "summary_hint": "Contains a 90-day auto-renewal clause with 100% fee hike, broad unilateral indemnity, customer data AI training rights, and binding arbitration.",
        "text": """ENTERPRISE CLOUD SAAS MASTER SERVICES AGREEMENT

This Master Services Agreement ("Agreement") is made effective as of January 15, 2026, by and between CloudPulse Enterprise Systems, Inc., a Delaware corporation ("Provider"), and the subscribing entity ("Customer").

SECTION 1: SUBSCRIPTION AND LICENSE GRANT
Provider hereby grants Customer a non-exclusive, non-transferable, revocable subscription license to access the CloudPulse Enterprise Intelligence Platform ("Platform") solely for Customer's internal business operations. Customer shall not reverse engineer, decompile, or create derivative works. Any violation shall incur immediate liquidated damages of $75,000 per occurrence.

SECTION 2: FEES, PAYMENT TERMS, AND AUTOMATIC SURCHARGES
(a) Fees shall be billed annually in advance. Invoices are payable within fifteen (15) days of receipt. Any balance unpaid after thirty (30) days shall accrue interest at the rate of 1.5% per month (18% per annum) or the maximum legal rate, plus a 5% administrative late penalty.
(b) Customer agrees to reimburse Provider for all costs of collection, including actual attorney's fees and litigation expenses incurred.

SECTION 3: TERM AND AUTOMATIC RENEWAL TRAP
This Agreement shall commence on the Effective Date and continue for an initial term of three (3) years ("Initial Term"). THIS AGREEMENT SHALL AUTOMATICALLY RENEW FOR SUCCESSIVE TWO (2) YEAR TERMS UNLESS CUSTOMER PROVIDES WRITTEN NOTICE OF NON-RENEWAL VIA CERTIFIED POSTAL MAIL NOT LESS THAN NINETY (90) DAYS PRIOR TO THE EXPIRATION OF THE CURRENT TERM. Upon any renewal, subscription fees shall automatically increase by twenty-five percent (25%) over the preceding term's rate.

SECTION 4: DATA USAGE, DERIVATIVE DATA, AND AI TRAINING
Customer grants Provider a perpetual, irrevocable, worldwide, royalty-free license to ingest, store, anonymize, aggregate, and process Customer Data for the purposes of training machine learning models, improving algorithms, and developing commercial analytics products. Provider shall retain sole ownership of all derived analytical models.

SECTION 5: UNILATERAL INDEMNIFICATION AND DEFENSE
Customer shall defend, indemnify, and hold harmless Provider, its officers, directors, employees, and affiliates from and against any and all claims, damages, liabilities, losses, costs, and expenses (including attorney's fees) arising out of or related to: (i) Customer's use of the Platform; (ii) any breach of Customer representations; or (iii) third-party claims alleging infringement caused by Customer data. Provider shall have no obligation to defend or indemnify Customer against third-party intellectual property claims.

SECTION 6: EXTREME LIMITATION OF LIABILITY
IN NO EVENT SHALL PROVIDER BE LIABLE FOR ANY INDIRECT, INCIDENTAL, CONSEQUENTIAL, SPECIAL, PUNITIVE, OR EXEMPLARY DAMAGES, INCLUDING LOSS OF PROFITS, DATA CORRUPTION, OR BUSINESS INTERRUPTION. PROVIDER'S MAXIMUM AGGREGATE LIABILITY UNDER THIS AGREEMENT SHALL BE STRICTLY CAPPED AT THE LESSER OF $1,000 OR THE FEES ACTUALLY PAID BY CUSTOMER IN THE ONE (1) MONTH PRECEDING THE EVENT GIVING RISE TO LIABILITY.

SECTION 7: TERMINATION FOR CONVENIENCE AND PENALTIES
Provider may terminate this Agreement for convenience at any time upon thirty (30) days written notice. Customer may NOT terminate for convenience. If Customer attempts to cancel or terminates without cause prior to term expiration, Customer shall immediately pay Provider an Early Termination Fee equal to one hundred percent (100%) of the remaining unpaid subscription fees for the unexpired term.

SECTION 8: DISPUTE RESOLUTION AND CLASS ACTION WAIVER
All disputes arising under or relating to this Agreement shall be resolved exclusively by binding confidential arbitration administered by JAMS in Wilmington, Delaware. CUSTOMER HEREBY EXPRESSLY WAIVES ANY RIGHT TO PARTICIPATE IN A CLASS ACTION LAWSUIT OR REPRESENTATIVE PROCEEDING AGAINST PROVIDER. Each party shall bear its own arbitration costs, except Customer shall pay Provider's costs if Provider prevails.
"""
    },
    {
        "id": "executive-employment",
        "title": "Executive Employment & Restrictive Covenants Agreement",
        "category": "Human Resources & Labor",
        "summary_hint": "Includes a 24-month worldwide non-compete, total assignment of side-project inventions, $100,000 liquidated damages, and clawback of bonuses.",
        "text": """EXECUTIVE EMPLOYMENT, CONFIDENTIALITY, AND RESTRICTIVE COVENANTS AGREEMENT

This Agreement is entered into on March 1, 2026, by and between Apex Hyperion Robotics Corp., a Delaware corporation ("Company"), and the undersigned individual ("Executive").

SECTION 1: AT-WILL EMPLOYMENT AND DUTIES
Executive shall serve as Vice President of AI Engineering. Employment with the Company is strictly at-will, meaning the Company may terminate Executive at any time, with or without cause, and without prior notice.

SECTION 2: COMPREHENSIVE INTELLECTUAL PROPERTY ASSIGNMENT
Executive agrees that all inventions, designs, algorithms, codebases, trade secrets, patents, and copyrighted materials conceived, developed, or reduced to practice by Executive—WHETHER OR NOT ON COMPANY TIME, ON COMPANY PREMISES, OR USING COMPANY EQUIPMENT, AND INCLUDING SIDE PROJECTS DEVELOPED ON PERSONAL COMPUTERS—during the term of employment shall belong exclusively and perpetually to Company. Executive hereby irrevocably assigns all rights, title, and interest therein to Company and waives all moral rights.

SECTION 3: NON-COMPETITION COVENANT (24 MONTHS WORLDWIDE)
During Executive's employment and for a period of twenty-four (24) months following the termination of employment for ANY reason (voluntary or involuntary):
Executive shall NOT directly or indirectly, whether as an employee, founder, consultant, investor, advisor, or contractor, engage in, perform services for, or assist any entity, business, or venture that develops, markets, or sells automated robotics, generative artificial intelligence, or related software anywhere in the world.

SECTION 4: NON-SOLICITATION OF CLIENTS AND TALENT
For a period of thirty-six (36) months post-termination, Executive shall not solicit, recruit, induce, or encourage any employee, contractor, vendor, or customer of Company to terminate or diminish their commercial relationship with Company.

SECTION 5: LIQUIDATED DAMAGES FOR BREACH
Executive acknowledges that any breach of Section 2, Section 3, or Section 4 will cause irreparable harm to Company. In the event of any breach or threatened breach, Executive shall immediately pay Company liquidated damages in the amount of One Hundred Thousand Dollars ($100,000) per violation, without prejudice to Company's right to obtain immediate ex-parte temporary restraining orders and permanent injunctions without posting any bond or security.

SECTION 6: INCENTIVE COMPENSATION CLAWBACK
Company reserves the unilateral right to claw back, cancel, or demand immediate refund of any bonuses, stock options, equity vesting, or performance incentives paid or granted to Executive within the preceding twenty-four (24) months if Company determines, in its sole discretion, that Executive committed misconduct, gross negligence, or violated company policies.

SECTION 7: GOVERNING LAW AND INJUNCTION RELIEF
This Agreement shall be governed by Delaware law. Executive consents to the exclusive personal jurisdiction of state and federal courts in New Castle County, Delaware. In any legal action brought by Company to enforce this Agreement, Executive shall reimburse Company for all legal fees and disbursements incurred.
"""
    },
    {
        "id": "commercial-lease",
        "title": "Triple-Net (NNN) Commercial Real Estate Lease Agreement",
        "category": "Real Estate & Leasing",
        "summary_hint": "Imposes triple-net pass-through expenses without audit rights, forfeiture of 3-month security deposit, 18% late fees, and full repair liability on tenant.",
        "text": """COMMERCIAL PROPERTY LEASE AGREEMENT (TRIPLE NET - NNN)

This Lease Agreement is executed on February 10, 2026, by and between Metro Tower Assets LLC ("Landlord"), and the leasing tenant ("Tenant").

SECTION 1: LEASED PREMISES AND INITIAL TERM
Landlord leases to Tenant Suite 400, consisting of 6,200 rentable square feet at 100 Financial Boulevard. The term shall be for sixty (60) months commencing April 1, 2026.

SECTION 2: BASE RENT AND ANNUAL ESCALATION
Tenant shall pay Base Rent of $22,000 per month, due on the first calendar day of each month. Rent shall automatically escalate by six percent (6%) compounding annually on each anniversary of the Commencement Date. If rent is not received by the 3rd of the month, a late fee of ten percent (10%) of the delinquent amount shall apply immediately, plus daily interest of 1.5% per month until fully paid.

SECTION 3: TRIPLE-NET (NNN) PASS-THROUGH EXPENSES
Tenant shall pay its proportionate share (18.5%) of ALL Operating Expenses, Real Estate Taxes, Capital Improvements, Roof Replacements, and Insurance Premiums incurred by Landlord for the building.
(a) Operating expenses are estimated by Landlord and reconciled annually. Tenant shall have NO RIGHT TO AUDIT or inspect Landlord's financial books or receipts.
(b) Tenant shall pay any reconciliation shortage within ten (10) days of Landlord's demand.

SECTION 4: MAINTENANCE AND STRUCTURAL REPAIRS
Tenant accepts the Premises in strict "AS-IS, WHERE-IS" condition with all faults. Tenant shall, at its sole cost, maintain, repair, and replace all HVAC units, plumbing fixtures, electrical systems, and structural window panels serving the Premises, regardless of age or pre-existing defects.

SECTION 5: SECURITY DEPOSIT FORFEITURE
Tenant has deposited with Landlord the sum of $66,000 as a Security Deposit. If Tenant breaches any covenant of this Lease, Landlord may immediately forfeit, retain, and commingle the entire Security Deposit without notice, and Tenant shall immediately replenish the full amount upon demand. The Security Deposit shall NOT bear interest and may be commingled with Landlord's general operating funds.

SECTION 6: PROHIBITION OF ASSIGNMENT AND SUBLETTING
Tenant shall not assign, sublease, mortgage, or transfer this Lease or any portion of the Premises without Landlord's prior written consent, which Landlord may withhold in its sole and arbitrary discretion. Any profit realized by Tenant from an approved sublease shall belong 100% to Landlord.

SECTION 7: LANDLORD'S REMEDIES AND ACCELERATION OF RENT
Upon any event of default by Tenant, Landlord may terminate this Lease, re-enter the Premises, and ACCELERATE AND DEMAND IMMEDIATE PAYMENT OF ALL REMAINING BASE RENT AND NNN CHARGES DUE FOR THE BALANCE OF THE 5-YEAR TERM, discounted at no more than 1%. Tenant waives all rights of redemption or stay of execution.
"""
    },
    {
        "id": "unilateral-nda",
        "title": "Unilateral Proprietary Information & Non-Disclosure Agreement",
        "category": "Corporate & Intellectual Property",
        "summary_hint": "Highly aggressive one-sided NDA: perpetual confidentiality, broad definition of trade secrets, $50k liquidated damages, and unilateral fee-shifting.",
        "text": """MUTUAL PROPRIETARY INFORMATION AND NON-DISCLOSURE AGREEMENT

This Agreement is entered into on April 5, 2026, by and between Titan Global Innovations LLC ("Disclosing Party") and the Recipient ("Receiving Party").

SECTION 1: DEFINITION OF CONFIDENTIAL INFORMATION
"Confidential Information" shall include all technical, financial, operational, marketing, customer, code, business strategies, ideas, inventions, discussions, and observations disclosed by Disclosing Party, whether oral, written, electronic, or visual, whether marked confidential or not. The mere fact that the parties are holding discussions is deemed strictly Confidential Information.

SECTION 2: OBLIGATIONS OF SECRECY AND USE RESTRICTIONS
Receiving Party shall hold all Confidential Information in strict trust and confidence. Receiving Party shall not use Confidential Information for any purpose other than evaluating a potential transaction with Disclosing Party. Receiving Party shall not disclose, copy, deconstruct, or disseminate Confidential Information to any person, including its own employees or legal counsel, without prior written approval from Disclosing Party.

SECTION 3: PERPETUAL DURATION OF CONFIDENTIALITY
The obligations of confidentiality under this Agreement shall NOT expire and shall remain in effect in perpetuity (forever), surviving any conclusion, termination, or abandonment of discussions between the parties.

SECTION 4: RETURN OR DESTRUCTION OF MATERIALS
Within forty-eight (48) hours of Disclosing Party's written request, Receiving Party shall return or destroy all documents, notes, memoranda, electronic files, and backups containing Confidential Information, and an executive officer of Receiving Party shall certify such destruction under penalty of perjury.

SECTION 5: INJUNCTIVE RELIEF AND LIQUIDATED DAMAGES
Receiving Party acknowledges that any disclosure or breach will cause catastrophic, irreparable damage. Disclosing Party shall be entitled to seek immediate injunctive relief and specific performance in any court of competent jurisdiction without proving monetary damages or posting a bond. In addition, Receiving Party shall pay Disclosing Party Fifty Thousand Dollars ($50,000) as agreed liquidated damages for each unauthorized disclosure or breach.

SECTION 6: UNILATERAL ATTORNEY'S FEES AND JURISDICTION
If Disclosing Party institutes any arbitration or legal proceeding to enforce this Agreement, Receiving Party shall pay all of Disclosing Party's attorney's fees, expert witness fees, and costs of litigation. This Agreement shall be governed by the laws of the State of New York.
"""
    }
]


def get_sample_by_id(sample_id: str) -> Dict[str, str]:
    for sample in SAMPLE_CONTRACTS:
        if sample["id"] == sample_id:
            return sample
    return SAMPLE_CONTRACTS[0]
