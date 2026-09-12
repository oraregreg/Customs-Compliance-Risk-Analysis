import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import random

# Set seed for reproducibility
np.random.seed(42)
random.seed(42)

# ========== Define Data Lists ==========

# Countries
countries = ['KENYA', 'SOUTH AFRICA', 'NIGERIA', 'EGYPT', 'GHANA', 'MOROCCO',
             'ETHIOPIA', 'TANZANIA', 'UGANDA', 'RWANDA', 'DRC', 'ZAMBIA',
             'MOZAMBIQUE', 'ANGOLA', 'SENEGAL', 'COTE DIVOIRE', 'CAMEROON',
             'CHINA', 'INDIA', 'USA', 'GERMANY', 'UK', 'UAE', 'TURKEY',
             'SOUTH KOREA', 'JAPAN', 'VIETNAM', 'THAILAND', 'MALAYSIA']

# High-risk origins (more likely to have delays)
high_risk_origins = ['CHINA', 'INDIA', 'TURKEY', 'VIETNAM', 'THAILAND']

# Suppliers
suppliers = ['TechGlobal Ltd', 'Industrial Supply Co', 'MediCare Solutions', 
             'AutoParts International', 'ChemCorp Industries', 'GreenEnergy Systems',
             'ElectroTech Manufacturing', 'PharmaLife Sciences', 'MetalWorks Foundry',
             'PlastiPack Ltd', 'AgriTech Solutions', 'TextileWorld Exports']

# Brokers (6 brokers)
brokers = ['DHL GLOBAL FORWARDING', 'KUEHNE NAGEL', 'BOLLORE LOGISTICS',
           'PANALPINA', 'EXPEDITORS INTERNATIONAL', 'AGILITY LOGISTICS']

# Ports (with some inherently slower)
ports = ['MOMBASA', 'DURBAN', 'LAGOS', 'ALEXANDRIA', 'CASABLANCA', 'PORT ELIZABETH',
         'CAPE TOWN', 'TEMA', 'ABIDJAN', 'DAR ES SALAAM', 'MOMBASA ICD', 'NAIROBI']

slow_ports = ['MOMBASA', 'LAGOS', 'ALEXANDRIA', 'CASABLANCA']

# HS Codes (with risk categories)
hs_codes = {
    '85': 'Electronics/Telecom',
    '84': 'Machinery/Industrial', 
    '87': 'Automotive',
    '30': 'Pharmaceuticals',
    '39': 'Plastics',
    '62': 'Textiles/Apparel',
    '73': 'Steel/Metal Products',
    '40': 'Rubber/Tyres',
    '94': 'Furniture/Bedding',
    '70': 'Glass'
}

# Product descriptions by category
product_descs = {
    '85': ['TELECOM EQUIPMENT', 'SWITCHING DEVICE', 'BATTERY MODULE', 'SOLAR PANEL', 'CABLE ASSEMBLY'],
    '84': ['INDUSTRIAL MACHINE', 'PUMP', 'COMPRESSOR', 'CONVEYOR BELT', 'GENERATOR'],
    '87': ['MOTOR VEHICLE PARTS', 'TYRES', 'BATTERY', 'ENGINE COMPONENT', 'BRAKE SYSTEM'],
    '30': ['MEDICINAL PREPARATIONS', 'VACCINES', 'ANTIBIOTICS', 'SURGICAL SUPPLIES', 'LAB REAGENTS'],
    '39': ['PLASTIC SHEETS', 'PACKAGING MATERIAL', 'PLASTIC COMPONENTS', 'PVC FILM', 'POLYTHENE BAGS'],
    '62': ['TEXTILE FABRIC', 'GARMENTS', 'CARPETS', 'LINEN', 'TEXTILE YARN'],
    '73': ['STEEL BARS', 'ALUMINIUM SHEETS', 'METAL FABRICATIONS', 'PIPES', 'WIRE PRODUCTS'],
    '40': ['RUBBER SHEETS', 'TYRES', 'RUBBER HOSES', 'CONVEYOR BELTS', 'RUBBER SEALS'],
    '94': ['FURNITURE', 'MATTRESSES', 'OFFICE CHAIRS', 'WOODEN FURNITURE', 'METAL FURNITURE'],
    '70': ['GLASS SHEETS', 'GLASS BOTTLES', 'WINDOW GLASS', 'GLASS TUBES', 'MIRRORS']
}

# Destinations
destinations = ['KENYA', 'SOUTH AFRICA', 'NIGERIA', 'GHANA', 'TANZANIA', 'UGANDA']

# FTA options
fta_options = ['EAC', 'AFCFTA', 'NONE', 'SADC', 'COMESA']

# Incoterms
incoterms = ['FOB', 'CIF', 'EXW', 'DAP', 'DDP', 'CFR']

# ========== Generate Dataset ==========

n = 5000
data = []

for i in range(n):
    # Determine destination
    dest = random.choice(destinations)
    
    # Brokers: 70% good, 20% medium, 10% bad (slow)
    broker_choice = random.choices(brokers, weights=[0.5, 0.2, 0.15, 0.05, 0.05, 0.05])[0]
    
    # Determine country of origin
    # 30% high-risk, 70% normal
    if random.random() < 0.3:
        origin = random.choice(high_risk_origins)
    else:
        origin = random.choice(countries)
    
    # HS Code category
    hs_category = random.choice(list(hs_codes.keys()))
    hs_code = hs_category + str(random.randint(1000, 9999))
    
    product_desc = random.choice(product_descs[hs_category])
    
    # Supplier
    supplier = random.choice(suppliers)
    
    # Port: 40% chance of slow port
    if random.random() < 0.4:
        port = random.choice(slow_ports)
    else:
        port = random.choice(ports)
    
    # Generate dates
    entry_date = datetime.now() - timedelta(days=random.randint(1, 365))
    is_weekend_entry = entry_date.weekday() >= 5
    
    # Values (generated before is_slow so declared-value scrutiny can factor in)
    # NOTE: generated as float (not int) so the later "extreme discrepancy" flaw
    # injection (which writes fractional values) doesn't hit a pandas dtype error.
    declared_value_usd = round(random.uniform(500, 150000), 2)
    
    # License requirement (defined before is_slow so missing licenses can drive delay)
    if hs_category == '30':
        license_required = 'Y' if random.random() < 0.3 else 'N'
    elif hs_category == '85':
        license_required = 'Y' if random.random() < 0.1 else 'N'
    else:
        license_required = 'N'
    license_obtained = 'Y' if (license_required == 'Y' and random.random() < 0.7) else 'N'
    license_missing = (license_required == 'Y' and license_obtained == 'N')
    
    # ===== Causal probability model for slow_clearance =====
    BROKER_SLOW_EFFECT = {
        'AGILITY LOGISTICS': -0.05,
        'KUEHNE NAGEL': -0.02,
        'BOLLORE LOGISTICS': 0.00,
        'PANALPINA': 0.02,
        'EXPEDITORS INTERNATIONAL': 0.04,
        'DHL GLOBAL FORWARDING': 0.06,
    }
    slow_prob = 0.08
    slow_prob += BROKER_SLOW_EFFECT[broker_choice]
    slow_prob += 0.15 if port in slow_ports else 0.0
    slow_prob += 0.08 if origin in high_risk_origins else 0.0
    slow_prob += 0.20 if license_missing else 0.0
    slow_prob += 0.05 if is_weekend_entry else 0.0
    slow_prob += 0.05 if declared_value_usd >= 135000 else 0.0  # top ~10% of the 500-150000 range
    slow_prob = min(max(slow_prob, 0.02), 0.95)
    
    is_slow = random.random() < slow_prob
    
    if is_slow:
        clearance_hours = random.randint(48, 120)
    else:
        clearance_hours = random.randint(2, 47)
    
    accepted_date = entry_date + timedelta(hours=random.randint(1, 5))
    release_date = entry_date + timedelta(hours=clearance_hours)
    
    # ===== Causal probability model for valuation discrepancy =====
    HIGH_RISK_SUPPLIERS = {'ChemCorp Industries', 'PlastiPack Ltd'}
    disc_prob = 0.06
    disc_prob += {'DHL GLOBAL FORWARDING': 0.05, 'EXPEDITORS INTERNATIONAL': 0.03,
                  'AGILITY LOGISTICS': -0.03}.get(broker_choice, 0.0)
    disc_prob += 0.10 if hs_category in ['85', '87', '73'] else 0.0
    disc_prob += 0.07 if origin in high_risk_origins else 0.0
    disc_prob += 0.08 if supplier in HIGH_RISK_SUPPLIERS else 0.0
    disc_prob = min(max(disc_prob, 0.02), 0.95)
    
    if random.random() < disc_prob:
        invoice_value_usd = declared_value_usd * random.uniform(1.25, 1.5)
    else:
        invoice_value_usd = declared_value_usd * random.uniform(0.95, 1.05)
    
    invoice_value_usd = round(invoice_value_usd, 2)
    
    # Duty rate varies by HS code and origin
    if hs_category in ['30', '85']:
        duty_rate = random.uniform(0.05, 0.15)  # Pharma and electronics
    elif hs_category in ['87', '73']:
        duty_rate = random.uniform(0.15, 0.25)  # Auto and steel
    else:
        duty_rate = random.uniform(0.05, 0.10)
    
    duty_amount_usd = round(declared_value_usd * duty_rate, 2)
    
    # Tax (VAT) ~16%
    tax_amount_usd = round((declared_value_usd + duty_amount_usd) * 0.16, 2)
    
    # Broker fee: varies by broker
    if broker_choice in ['DHL GLOBAL FORWARDING', 'KUEHNE NAGEL']:
        broker_fee_usd = round(random.uniform(150, 300), 2)
    elif broker_choice in ['BOLLORE LOGISTICS', 'PANALPINA']:
        broker_fee_usd = round(random.uniform(200, 450), 2)
    else:
        broker_fee_usd = round(random.uniform(100, 400), 2)
    
    # FTA claimed
    fta_claimed = random.choice(fta_options)
    
    # Restricted party pass (99% pass)
    restricted_party_pass = 'Y' if random.random() < 0.99 else 'N'
    
    # Incoterm
    incoterm = random.choice(incoterms)
    
    # Weight and volume
    weight_kg = round(random.uniform(10, 5000), 2)
    volume_m3 = round(random.uniform(0.1, 20), 2)
    
    # Container number
    container_number = f'AMZN{random.randint(100000, 999999)}'
    
    # Add flaws
    row = {
        'shipment_id': f'SHIP{str(i+1).zfill(6)}',
        'entry_no': f'22EMKIM{str(random.randint(400000, 499999))}',
        'hs_code': hs_code,
        'product_desc': product_desc,
        'supplier': supplier,
        'country_origin': origin,
        'country_destination': dest,
        'declared_value_usd': declared_value_usd,
        'invoice_value_usd': invoice_value_usd,
        'weight_kg': weight_kg,
        'volume_m3': volume_m3,
        'broker': broker_choice,
        'port_of_entry': port,
        'entry_date': entry_date.strftime('%Y-%m-%d %H:%M:%S'),
        'accepted_date': accepted_date.strftime('%Y-%m-%d %H:%M:%S'),
        'release_date': release_date.strftime('%Y-%m-%d %H:%M:%S'),
        'duty_amount_usd': duty_amount_usd,
        'tax_amount_usd': tax_amount_usd,
        'broker_fee_usd': broker_fee_usd,
        'incoterm': incoterm,
        'license_required': license_required,
        'license_obtained': license_obtained,
        'fta_claimed': fta_claimed,
        'restricted_party_pass': restricted_party_pass,
        'container_number': container_number,
        'slow_clearance': 'Y' if is_slow else 'N'
    }
    data.append(row)

# Create DataFrame
df = pd.DataFrame(data)

# ========== Add Specific Flaws ==========

# 1. Missing values (5% HS codes missing)
missing_hs_idx = np.random.choice(df.index, size=int(0.05 * n), replace=False)
df.loc[missing_hs_idx, 'hs_code'] = None

# 2. Missing countries (3%)
missing_country_idx = np.random.choice(df.index, size=int(0.03 * n), replace=False)
df.loc[missing_country_idx, 'country_origin'] = None

# 3. Missing dates (2%)
missing_date_idx = np.random.choice(df.index, size=int(0.02 * n), replace=False)
df.loc[missing_date_idx, 'release_date'] = None

# 4. Outliers (extreme weights)
outlier_idx = np.random.choice(df.index, size=int(0.02 * n), replace=False)
df.loc[outlier_idx, 'weight_kg'] = random.uniform(50000, 150000)

# 5. Invalid dates (release before entry)
invalid_date_idx = np.random.choice(df.index, size=int(0.02 * n), replace=False)
df.loc[invalid_date_idx, 'release_date'] = df.loc[invalid_date_idx, 'entry_date']

# 6. Duplicates (5% duplicate entry numbers)
dup_indices = np.random.choice(df.index, size=int(0.05 * n), replace=False)
for idx in dup_indices:
    # Create duplicate by copying the row and modifying shipment_id
    dup_row = df.loc[idx].copy()
    dup_row['shipment_id'] = f'SHIP{str(random.randint(200000, 299999)).zfill(6)}'
    df = pd.concat([df, pd.DataFrame([dup_row])], ignore_index=True)

# 7. Incorrect HS code lengths (2% wrong digit count)
incorrect_hs_idx = np.random.choice(df.index, size=int(0.02 * n), replace=False)
df.loc[incorrect_hs_idx, 'hs_code'] = df.loc[incorrect_hs_idx, 'hs_code'].astype(str) + 'X'

# 8. Case inconsistencies in text fields
inconsistent_idx = np.random.choice(df.index, size=int(0.05 * n), replace=False)
df.loc[inconsistent_idx, 'country_origin'] = df.loc[inconsistent_idx, 'country_origin'].str.lower()
df.loc[inconsistent_idx, 'broker'] = df.loc[inconsistent_idx, 'broker'].str.lower()

# Random extra spaces
extra_space_idx = np.random.choice(df.index, size=int(0.03 * n), replace=False)
df.loc[extra_space_idx, 'port_of_entry'] = ' ' + df.loc[extra_space_idx, 'port_of_entry'] + ' '

# 9. Valuation discrepancies (some are extreme)
extreme_disc_idx = np.random.choice(df.index, size=int(0.03 * n), replace=False)
df.loc[extreme_disc_idx, 'declared_value_usd'] = df.loc[extreme_disc_idx, 'invoice_value_usd'] * 0.5

# 10. Slow clearance already built into the data via 'slow_clearance' flag

# Reset index
df = df.reset_index(drop=True)

# Save to CSV
df.to_csv('customs_clearance_data.csv', index=False)
print(f"Dataset generated with {len(df)} rows and {len(df.columns)} columns.")