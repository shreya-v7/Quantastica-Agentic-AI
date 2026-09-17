"""Indian income tax rule tables for AY 2025-26 (FY 2024-25). Amounts in INR.

Slabs are (upper_bound, rate) pairs; None upper bound means no limit. Surcharge bands
are (income_threshold, rate). Marginal relief applies at each surcharge threshold.
"""

ASSESSMENT_YEAR = "2025-26"

OLD_REGIME = {
    "slabs": [(250_000, 0.0), (500_000, 0.05), (1_000_000, 0.20), (None, 0.30)],
    "standard_deduction": 50_000,
    "rebate_87a_income_cap": 500_000,
    "rebate_87a_max": 12_500,
    "surcharge": [(50_000_000, 0.37), (20_000_000, 0.25), (10_000_000, 0.15), (5_000_000, 0.10)],
    "cess": 0.04,
}

NEW_REGIME = {
    "slabs": [
        (300_000, 0.0),
        (700_000, 0.05),
        (1_000_000, 0.10),
        (1_200_000, 0.15),
        (1_500_000, 0.20),
        (None, 0.30),
    ],
    "standard_deduction": 75_000,
    "rebate_87a_income_cap": 700_000,
    "rebate_87a_max": 25_000,
    # New regime caps surcharge at 25 percent.
    "surcharge": [(20_000_000, 0.25), (10_000_000, 0.15), (5_000_000, 0.10)],
    "cess": 0.04,
}

DEDUCTION_CAPS = {
    "80c": 150_000,
    "80d_self_below_60": 25_000,
    "80d_self_60_plus": 50_000,
    "80ccd_1b": 50_000,
    "24b_self_occupied": 200_000,
}

CAPITAL_GAINS = {
    # Post 23 July 2024 rates for listed equity and equity MF.
    "equity_stcg_rate": 0.20,
    "equity_ltcg_rate": 0.125,
    "equity_ltcg_exemption": 125_000,
    "ltcg_grandfather_date": "2018-01-31",
    # Debt funds bought after 1 Apr 2023: gains taxed at slab rate.
    "debt_at_slab": True,
}
