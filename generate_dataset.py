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
    
    # Clearance time: normal is 2-48 hours, slow is 48-120 hours
    if random.random() < 0.15:  # 15% slow clearance
        clearance_hours = random.randint(48, 120)
        is_slow = True
    else:
        clearance_hours = random.randint(2, 47)
        is_slow = False
    
    accepted_date = entry_date + timedelta(hours=random.randint(1, 5))
    release_date = entry_date + timedelta(hours=clearance_hours)
    
    # Values
    declared_value_usd = random.randint(500, 150000)
    # 20% of shipments have valuation discrepancy >20%
    if random.random() < 0.2:
        invoice_value_usd = declared_value_usd * random.uniform(1.25, 1.5)
    else:
        invoice_value_usd = declared_value_usd * random.uniform(0.95, 1.05)
    
    invoice_value_usd = round(invoice_value_usd, 2)
    declared_value_usd = round(declared_value_usd, 2)
    
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
    
    # License requirement (10% of pharma, 5% electronics)
    if hs_category == '30':
        license_required = 'Y' if random.random() < 0.3 else 'N'
    elif hs_category == '85':
        license_required = 'Y' if random.random() < 0.1 else 'N'
    else:
        license_required = 'N'
    
    license_obtained = 'Y' if (license_required == 'Y' and random.random() < 0.7) else 'N'
    
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

