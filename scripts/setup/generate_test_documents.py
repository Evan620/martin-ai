#!/usr/bin/env python3
"""
Generate test documents as plain text files (NO DEPENDENCIES REQUIRED).

Uses only Python standard library - no external packages needed.
"""

from pathlib import Path
from datetime import datetime


def create_text_document(output_path, title, content):
    """Create a text document."""
    lines = []
    
    # Header
    lines.append("=" * 80)
    lines.append(title.center(80))
    lines.append("=" * 80)
    lines.append("")
    
    # Metadata
    lines.append(f"Document Type: {content.get('type', 'Policy Document')}")
    lines.append(f"Date: {content.get('date', datetime.now().strftime('%B %d, %Y'))}")
    lines.append(f"Organization: {content.get('org', 'ECOWAS')}")
    if 'country' in content:
        lines.append(f"Country: {content['country']}")
    if 'sector' in content:
        lines.append(f"Sector: {content['sector']}")
    lines.append("")
    lines.append("-" * 80)
    lines.append("")
    
    # Executive Summary
    if 'executive_summary' in content:
        lines.append("EXECUTIVE SUMMARY")
        lines.append("")
        lines.append(content['executive_summary'])
        lines.append("")
        lines.append("-" * 80)
        lines.append("")
    
    # Sections
    for section_title, section_content in content.get('sections', {}).items():
        lines.append(section_title.upper())
        lines.append("")
        
        if isinstance(section_content, list):
            for item in section_content:
                lines.append(f"  • {item}")
            lines.append("")
        else:
            # Wrap text at 80 characters
            words = section_content.split()
            current_line = []
            current_length = 0
            
            for word in words:
                if current_length + len(word) + 1 > 78:
                    lines.append(" ".join(current_line))
                    current_line = [word]
                    current_length = len(word)
                else:
                    current_line.append(word)
                    current_length += len(word) + 1
            
            if current_line:
                lines.append(" ".join(current_line))
            lines.append("")
        
        lines.append("")
    
    # Footer
    lines.append("=" * 80)
    lines.append(f"End of Document - {output_path.stem}")
    lines.append("=" * 80)
    
    # Write to file
    output_path.write_text("\n".join(lines), encoding='utf-8')
    print(f"✓ Created: {output_path.name}")


def main():
    """Generate all test documents."""
    output_dir = Path(__file__).parent.parent.parent / "data" / "raw"
    output_dir.mkdir(parents=True, exist_ok=True)
    
    print("=" * 60)
    print("ECOWAS Summit - Test Document Generation")
    print("=" * 60)
    print()
    
    documents = [
        # 1. ECOWAS Treaty
        {
            'filename': 'ECOWAS_Treaty_Revised_1993.txt',
            'title': 'TREATY OF THE ECONOMIC COMMUNITY OF WEST AFRICAN STATES (ECOWAS)',
            'content': {
                'type': 'Treaty',
                'date': 'July 24, 1993',
                'org': 'ECOWAS',
                'sections': {
                    'Preamble': """The Heads of State and Government of West African States, convinced of the need to promote economic integration and cooperation among member states to accelerate economic development and improve the living standards of their peoples, have agreed to establish the Economic Community of West African States.""",
                    
                    'Article 1 - Establishment': """There is hereby established among the High Contracting Parties an Economic Community of West African States (ECOWAS) with the aim of promoting cooperation and integration, leading to the establishment of an economic union in West Africa in order to raise the living standards of its peoples, maintain and enhance economic stability, foster relations among Member States and contribute to the progress and development of the African Continent.""",
                    
                    'Article 3 - Aims and Objectives': [
                        'Promote cooperation and integration in economic, social and cultural activities',
                        'Raise the standard of living of the peoples of Member States',
                        'Increase and maintain economic stability and foster closer relations among Member States',
                        'Contribute to the progress and development of the African continent',
                        'Establish a common market through free movement of goods, services, capital, and people',
                        'Harmonize agricultural, industrial, transport, and telecommunications policies',
                        'Promote joint development of natural resources for the benefit of Member States'
                    ],
                    
                    'Article 56 - Natural Resources': """Member States undertake to pursue, individually and collectively, policies aimed at the rational exploitation and optimal utilization of their natural resources, including minerals, energy, and agricultural resources. They shall cooperate in the development of joint projects for resource extraction, processing, and value addition to maximize benefits for their peoples.""",
                }
            }
        },
        
        # 2. ECOWAS Vision 2050
        {
            'filename': 'ECOWAS_Vision_2050.txt',
            'title': 'ECOWAS VISION 2050 - THE FUTURE WE WANT',
            'content': {
                'type': 'Policy Document',
                'date': 'January 2020',
                'org': 'ECOWAS Commission',
                'executive_summary': """ECOWAS Vision 2050 articulates the long-term aspirations of West African peoples for a borderless, peaceful, prosperous and cohesive region, built on good governance and where people have the capacity to access and harness its enormous resources through the creation of opportunities for sustainable development and environmental preservation. This vision builds on the achievements of Vision 2020 and addresses emerging challenges including climate change, technological disruption, and demographic shifts.""",
                'sections': {
                    '1. Strategic Pillars': """The Vision 2050 is anchored on five strategic pillars: (1) Economic Integration and Prosperity - creating a single market with free movement of goods, services, capital, and people; (2) Infrastructure Development - building world-class transport, energy, and digital infrastructure; (3) Human Capital Development - investing in education, health, and skills for the 21st century; (4) Governance and Peace - strengthening democratic institutions and conflict prevention mechanisms; (5) Environmental Sustainability - transitioning to green economies and climate resilience.""",
                    
                    '2. Economic Transformation': """By 2050, ECOWAS aims to achieve a GDP of $5 trillion, making West Africa one of the world's top 10 economic regions. This will be driven by industrialization, value addition in agriculture and mining, development of the digital economy, and expansion of intra-regional trade to 50% of total trade. Key sectors include agro-processing, renewable energy, manufacturing, tourism, and creative industries.""",
                    
                    '3. Mineral Resources Development': """ECOWAS will transform its mineral wealth into sustainable prosperity through local value addition, beneficiation, and downstream processing. The region possesses significant deposits of gold, diamonds, bauxite, iron ore, manganese, phosphates, and rare earth elements. Vision 2050 calls for establishing regional mineral processing hubs, developing local manufacturing capacity for mining equipment, and ensuring environmental and social governance standards.""",
                    
                    '4. Energy Transition': """The region will transition to 60% renewable energy by 2050, leveraging abundant solar, wind, hydro, and biomass resources. This includes developing 50 GW of solar capacity, 20 GW of wind, and 30 GW of hydropower. Regional energy markets will enable cross-border electricity trade, while mini-grids and off-grid solutions will ensure universal energy access in rural areas.""",
                    
                    '5. Agricultural Transformation': """Agriculture will be modernized through mechanization, irrigation, improved seeds, and digital agriculture. The region will achieve food self-sufficiency and become a net exporter of processed agricultural products. Priority value chains include cocoa, cashew, cotton, rice, cassava, and livestock. Climate-smart agriculture practices will ensure resilience to climate change.""",
                }
            }
        },
        
        # 3. Mining Vision
        {
            'filename': 'ECOWAS_Mining_Vision_2025.txt',
            'title': 'ECOWAS MINING VISION AND ACTION PLAN',
            'content': {
                'type': 'Policy Document',
                'date': 'March 2025',
                'org': 'ECOWAS Commission',
                'sector': 'Minerals',
                'executive_summary': """The ECOWAS Mining Vision provides a framework for transparent, equitable and optimal exploitation of mineral resources to underpin broad-based sustainable growth and socio-economic development. It aligns with the African Mining Vision and addresses the paradox of mineral wealth coexisting with widespread poverty. The vision emphasizes local value addition, environmental sustainability, and equitable benefit sharing.""",
                'sections': {
                    '1. Regional Mineral Endowment': """West Africa is endowed with world-class mineral deposits including 30% of global bauxite reserves, significant gold deposits in Ghana, Mali, Burkina Faso, and Guinea, diamonds in Sierra Leone and Liberia, iron ore in Guinea, Liberia, and Sierra Leone, manganese in Ghana and Côte d'Ivoire, phosphates in Togo and Senegal, and emerging lithium and rare earth discoveries. The total value of mineral resources is estimated at over $2 trillion.""",
                    
                    '2. Value Addition and Beneficiation': """Member States commit to policies promoting local processing and beneficiation of minerals. This includes establishing regional smelters for bauxite-to-aluminum processing, gold refineries, diamond cutting and polishing centers, and steel mills. Export bans or taxes on raw minerals will incentivize local value addition. Regional mineral processing hubs will be developed in strategic locations with access to energy and transport infrastructure.""",
                    
                    '3. Artisanal and Small-Scale Mining': """ASM employs over 5 million people in the region and contributes significantly to rural livelihoods. The vision calls for formalizing ASM through simplified licensing, providing technical and financial support, ensuring environmental compliance, and eliminating child labor and mercury use. ASM zones will be designated, and cooperatives will be strengthened to improve bargaining power and access to markets.""",
                    
                    '4. Environmental and Social Governance': """Mining operations must adhere to strict environmental standards including Environmental Impact Assessments, mine closure plans, and rehabilitation bonds. Free, Prior and Informed Consent of affected communities is mandatory. Mining revenues will be transparently managed through the Extractive Industries Transparency Initiative. Community development agreements will ensure local benefits from mining activities.""",
                }
            }
        },
        
        # 4. Renewable Energy Policy
        {
            'filename': 'ECOWAS_Renewable_Energy_Policy_2023.txt',
            'title': 'ECOWAS RENEWABLE ENERGY POLICY (EREP)',
            'content': {
                'type': 'Policy Document',
                'date': 'June 2023',
                'org': 'ECOWAS Centre for Renewable Energy and Energy Efficiency',
                'sector': 'Energy',
                'executive_summary': """The ECOWAS Renewable Energy Policy aims to increase the share of renewable energy in the regional energy mix to 35% by 2030 and 60% by 2050. This policy addresses energy poverty affecting over 200 million people in the region while contributing to climate change mitigation. It promotes solar, wind, hydro, biomass, and geothermal energy development through enabling policies, financing mechanisms, and regional cooperation.""",
                'sections': {
                    '1. Energy Access Challenge': """Despite abundant renewable energy resources, only 52% of the West African population has access to electricity, with rural electrification rates below 30% in many countries. Over 80% of the population relies on traditional biomass for cooking, leading to deforestation and health impacts. The region needs to add 50 GW of generation capacity by 2030 to meet growing demand and achieve universal energy access.""",
                    
                    '2. Renewable Energy Potential': """West Africa has exceptional renewable energy resources: solar irradiation of 4-6 kWh/m²/day enabling 1,000 GW of solar potential, wind resources of 15 GW particularly in coastal and Sahel regions, 20 GW of untapped hydropower, and abundant biomass from agricultural residues. Geothermal potential exists in volcanic regions. These resources can meet regional energy needs many times over.""",
                    
                    '3. Policy Measures': """Member States will implement feed-in tariffs, net metering, tax incentives for renewable energy investments, and competitive auctions for large-scale projects. Renewable energy targets will be integrated into national energy plans. Regulatory frameworks will be streamlined to reduce project development timelines. Grid codes will be updated to accommodate variable renewable energy. Energy storage systems will be promoted to ensure grid stability.""",
                    
                    '4. West African Power Pool': """WAPP will facilitate cross-border electricity trade, enabling countries with surplus renewable energy to export to deficit countries. Regional transmission infrastructure will be expanded, including the North Core, Coastal, and CLSG interconnections. A regional electricity market will be established with transparent pricing and dispatch mechanisms.""",
                }
            }
        },
        
        # 5. Agricultural Policy
        {
            'filename': 'ECOWAS_Agricultural_Policy_ECOWAP_2025.txt',
            'title': 'ECOWAS AGRICULTURAL POLICY (ECOWAP)',
            'content': {
                'type': 'Policy Document',
                'date': 'February 2025',
                'org': 'ECOWAS Commission - Agriculture Department',
                'sector': 'Agriculture',
                'executive_summary': """ECOWAP aims to transform West African agriculture into a modern, competitive, and sustainable sector that ensures food security, creates jobs, and generates income for rural populations. The policy focuses on increasing productivity, developing value chains, improving market access, and building resilience to climate change. It aligns with the Comprehensive Africa Agriculture Development Programme and the Malabo Declaration commitments.""",
                'sections': {
                    '1. Agricultural Potential': """West Africa has 400 million hectares of arable land, of which only 25% is currently cultivated. The region has diverse agro-ecological zones supporting crops including rice, maize, cassava, yams, cocoa, coffee, cotton, cashew, and shea. Livestock populations include 80 million cattle, 150 million sheep and goats. Fisheries resources in coastal and inland waters support millions of livelihoods. With proper investments, the region can feed itself and become a major agricultural exporter.""",
                    
                    '2. Productivity Enhancement': """Average crop yields in West Africa are 30-50% below global averages due to limited use of improved seeds, fertilizers, and mechanization. ECOWAP promotes the adoption of high-yielding varieties, integrated soil fertility management, irrigation development, and agricultural mechanization. Extension services will be strengthened to reach smallholder farmers. Digital agriculture tools including weather forecasts, market information, and agronomic advice will be scaled up.""",
                    
                    '3. Value Chain Development': """Priority value chains include cocoa (60% of global production), cashew (40% of global production), cotton, rice, cassava, and livestock. The policy promotes local processing to capture more value. For example, processing cocoa into chocolate, cashew into kernels and derivatives, and cotton into textiles. Agro-processing zones will be established with infrastructure and incentives. Quality standards will ensure competitiveness in international markets.""",
                    
                    '4. Climate-Smart Agriculture': """Climate change threatens agricultural productivity through droughts, floods, and changing rainfall patterns. ECOWAP promotes climate-smart practices including drought-resistant varieties, conservation agriculture, agroforestry, and integrated crop-livestock systems. Weather-indexed insurance will protect farmers from climate risks. Early warning systems will enable timely responses to climate shocks.""",
                }
            }
        },
        
        # 6. Guinea Bauxite Project
        {
            'filename': 'Guinea_Bauxite_Alumina_Refinery_Feasibility_Study_2024.txt',
            'title': 'GUINEA BAUXITE-TO-ALUMINA REFINERY PROJECT - FEASIBILITY STUDY',
            'content': {
                'type': 'Feasibility Study',
                'date': 'March 2024',
                'org': 'ECOWAS Investment Facilitation Unit',
                'country': 'Guinea',
                'sector': 'Minerals',
                'executive_summary': """This feasibility study examines the development of an integrated bauxite mining and alumina refining complex in the Boke region of Guinea. Guinea possesses the world's largest bauxite reserves (7.4 billion tonnes, representing 25% of global reserves). Currently, 95% of Guinean bauxite is exported as raw ore, with minimal value addition. This $2.5 billion project will establish a 2 million tonne per annum alumina refinery, creating 3,500 direct jobs and generating $800 million in annual export revenues.""",
                'sections': {
                    'Project Overview': """The Boke Bauxite Processing Complex will process 6 million tonnes per annum of bauxite ore to produce 2 million tonnes of smelter-grade alumina using the Bayer process. Energy will be supplied by a dedicated 150 MW combined-cycle gas power plant, with potential future connection to the Kaleta hydropower station. Total capital expenditure is estimated at $2.5 billion with an expected Internal Rate of Return of 18.5%.""",
                    
                    'Market Analysis': """Global alumina demand is projected to grow at 3.2% annually, driven by aluminum consumption in automotive, construction, and packaging sectors. China accounts for 55% of global alumina production but is increasingly importing due to environmental regulations. Guinea's proximity to European and North American markets provides a competitive advantage. The project will target long-term offtake agreements with aluminum smelters in Europe, North America, and Asia.""",
                    
                    'Technical Design': """The refinery will use the Bayer process to convert bauxite ore into alumina. Key infrastructure includes crushing and grinding facilities, digestion tanks, clarification and filtration systems, precipitation and calcination units, and red mud storage facilities. The plant will process 6 million tonnes of bauxite ore to produce 2 million tonnes of smelter-grade alumina annually.""",
                    
                    'Economic Impact': """At an alumina price of $400 per tonne, the project generates a Net Present Value of $1.2 billion at a 10% discount rate and an Internal Rate of Return of 18.5%. Operating costs are projected at $280 per tonne of alumina, competitive with global benchmarks. The project will contribute $150 million annually in taxes and royalties to the Guinean government and create significant value addition compared to raw bauxite exports.""",
                }
            }
        },
        
        # 7. Sahel Solar Project
        {
            'filename': 'Sahel_Solar_Belt_Regional_Energy_Project_2024.txt',
            'title': 'SAHEL SOLAR BELT - REGIONAL RENEWABLE ENERGY PROJECT',
            'content': {
                'type': 'Feasibility Study',
                'date': 'April 2024',
                'org': 'West African Power Pool',
                'country': 'Multi-country (Mali, Burkina Faso, Niger)',
                'sector': 'Energy',
                'executive_summary': """The Sahel Solar Belt is a transformative regional project to develop 2,000 MW of utility-scale solar photovoltaic capacity across Mali, Burkina Faso, and Niger. The Sahel region has exceptional solar resources (6-7 kWh/m²/day) but faces severe energy poverty, with electrification rates below 30%. This $4.2 billion project will provide clean, affordable electricity to 5 million people, reduce diesel dependence, and enable cross-border power trade through the West African Power Pool.""",
                'sections': {
                    'Technical Configuration': """The project comprises six solar parks of 300-400 MW each, strategically located near demand centers and transmission infrastructure: Bamako Solar Park (Mali) - 400 MW, Sikasso Solar Park (Mali) - 300 MW, Ouagadougou Solar Park (Burkina Faso) - 400 MW, Bobo-Dioulasso Solar Park (Burkina Faso) - 300 MW, Niamey Solar Park (Niger) - 400 MW, and Maradi Solar Park (Niger) - 200 MW. Each park will include bifacial solar modules, single-axis tracking systems, and 4-hour battery energy storage systems totaling 1,000 MWh to ensure dispatchability.""",
                    
                    'Economic Analysis': """Total project cost is $4.2 billion ($2.10 per Watt including storage), comprising $3.5 billion for solar and storage systems, $500 million for grid connection, and $200 million for project development and contingencies. Levelized Cost of Electricity is estimated at $0.045 per kWh, highly competitive with diesel generation ($0.25 per kWh) and grid electricity ($0.15 per kWh). Power Purchase Agreements will be signed with national utilities at $0.06 per kWh for 25 years, with sovereign guarantees and World Bank Partial Risk Guarantees.""",
                    
                    'Climate Impact': """The project will avoid 1.5 million tonnes of CO2 emissions annually, equivalent to removing 300,000 cars from roads. It will displace 400 million liters of diesel fuel, saving $300 million in import costs. Reliable electricity will enable productive uses including irrigation, cold storage, and manufacturing, creating 50,000 indirect jobs. The project aligns with NDC commitments of all three countries and will generate carbon credits under Article 6 of the Paris Agreement.""",
                }
            }
        },
        
        # 8. Cashew Processing
        {
            'filename': 'Cote_dIvoire_Cashew_Processing_Industrial_Park_2024.txt',
            'title': "CÔTE D'IVOIRE CASHEW PROCESSING INDUSTRIAL PARK",
            'content': {
                'type': 'Feasibility Study',
                'date': 'May 2024',
                'org': 'ECOWAS Agribusiness Development Agency',
                'country': "Côte d'Ivoire",
                'sector': 'Agriculture',
                'executive_summary': """The Abidjan Cashew Processing Zone will establish an integrated industrial park with capacity to process 100,000 tonnes of raw cashew nuts annually, producing 25,000 tonnes of cashew kernels and 75,000 tonnes of cashew nut shell liquid. This $150 million project will create 8,000 direct jobs, 80% of which will be for women, and enable Côte d'Ivoire to capture more value from its position as the world's largest cashew producer.""",
                'sections': {
                    'Sector Context': """Côte d'Ivoire is the world's largest producer of raw cashew nuts, accounting for 25% of global production with 850,000 tonnes in 2023. However, 90% of raw cashew nuts are exported to Vietnam and India for processing, with Ivorian processors capturing only 10% of production. This represents a massive loss of value addition potential, as processed cashew kernels sell for 3-4 times the price of raw nuts. The government has set a target to process 50% of raw cashew nut production domestically by 2025.""",
                    
                    'Processing Technology': """The project will use semi-automated processing technology optimized for African conditions. Key stages include cleaning and grading, steam cooking, shelling (combination of mechanical and manual), drying, peeling, grading and sorting, and packaging. Cashew nut shell liquid will be extracted during roasting and sold as a byproduct for use in resins, paints, and biofuels. Automation will be introduced in cleaning, cooking, and grading, while shelling and peeling will remain labor-intensive to maximize employment.""",
                    
                    'Market and Offtake': """Global cashew kernel demand is growing at 5% annually, driven by health trends and snack food consumption. Premium markets in Europe and North America pay $8-12 per kg for high-quality kernels. The project will target Fair Trade and organic certifications to access premium segments. Long-term offtake agreements have been secured with European importers for 60% of production. The remaining 40% will be sold through spot markets and domestic consumption.""",
                    
                    'Financial Projections': """Total investment is $150 million, including $100 million for processing equipment, $30 million for buildings and infrastructure, and $20 million for working capital. Operating costs are estimated at $6,500 per tonne of kernels. At a kernel selling price of $9,000 per tonne, the project generates annual revenues of $225 million and EBITDA of $62 million. Net Present Value is $180 million at 12% discount rate with Internal Rate of Return of 22.3%. Payback period is 6 years.""",
                }
            }
        },
        
        # 9. Highway Project
        {
            'filename': 'Abidjan_Lagos_Corridor_Highway_Project_2024.txt',
            'title': 'ABIDJAN-LAGOS CORRIDOR HIGHWAY DEVELOPMENT PROJECT',
            'content': {
                'type': 'Feasibility Study',
                'date': 'June 2024',
                'org': 'ECOWAS Infrastructure Development Authority',
                'country': "Multi-country (Côte d'Ivoire, Ghana, Togo, Benin, Nigeria)",
                'sector': 'Infrastructure',
                'executive_summary': """The Abidjan-Lagos corridor is the economic backbone of West Africa, connecting five countries with a combined population of 300 million and GDP of $800 billion. The corridor accounts for 75% of the region's international trade and 60% of intra-regional trade. This $15.6 billion project will develop a modern 6-lane highway spanning 1,028 km, reducing travel time from 30+ hours to 10 hours and generating $9 billion in annual economic benefits.""",
                'sections': {
                    'Project Scope': """The highway will span 1,028 km from Abidjan (Côte d'Ivoire) to Lagos (Nigeria), passing through Accra (Ghana), Lomé (Togo), and Cotonou (Benin). Key features include 6-lane divided carriageway with 3.5m lanes and 3m shoulders, 45 interchanges at major cities and border crossings, 15 toll plazas with electronic toll collection, 8 rest areas with fuel stations and amenities, 120 km of bypasses around major cities, and 25 bridges including a new 2 km bridge over the Volta River.""",
                    
                    'Border Facilitation': """A critical component is the modernization of border crossings to reduce delays. Currently, trucks spend 2-5 days at each border due to customs procedures and inspections. The project includes One-Stop Border Posts with joint customs and immigration, electronic cargo tracking systems, pre-clearance facilities, dedicated truck parking and inspection areas, and harmonized documentation under the ECOWAS Trade Liberalization Scheme. These measures will reduce border crossing time to under 2 hours.""",
                    
                    'Economic Benefits': """The highway will generate substantial economic benefits: Transport cost reduction from $0.15 per tonne-km to $0.08 per tonne-km, saving $2 billion annually; Travel time savings worth $1.5 billion annually; Trade facilitation enabling $5 billion in additional intra-regional trade; Accident reduction saving 500 lives and $200 million annually; and Induced development along the corridor creating 500,000 jobs. Total economic benefits are estimated at $9 billion annually.""",
                    
                    'Financing Structure': """The $15.6 billion investment will be financed through a Public-Private Partnership with a 30-year concession. Financing sources include $4 billion equity from consortium members, $8 billion senior debt from multilateral development banks, $2.6 billion mezzanine finance and export credit agencies, and $1 billion from ECOWAS Regional Development Fund. Toll revenues of $800 million per year and availability payments from governments will service the debt.""",
                }
            }
        },
        
        # 10. Digital Backbone
        {
            'filename': 'West_Africa_Digital_Backbone_Broadband_Project_2024.txt',
            'title': 'WEST AFRICA DIGITAL BACKBONE - REGIONAL BROADBAND PROJECT',
            'content': {
                'type': 'Feasibility Study',
                'date': 'July 2024',
                'org': 'ECOWAS Digital Economy Commission',
                'country': 'Regional (15 ECOWAS countries)',
                'sector': 'Digital Infrastructure',
                'executive_summary': """The ECOWAS Digital Backbone will deploy 50,000 km of fiber optic cable connecting all capital cities, secondary cities, and border crossings. This $3.8 billion project will provide high-speed, affordable internet to governments, businesses, and citizens, enabling a $50 billion digital economy by 2030. The network will be carrier-neutral, providing open access to all licensed operators and reducing broadband costs by 80%.""",
                'sections': {
                    'Digital Divide Challenge': """West Africa faces a severe digital divide, with only 35% internet penetration compared to 65% globally. Broadband access is even lower at 15%, concentrated in urban areas. High costs ($50 per month for 10 Mbps) and limited infrastructure prevent digital inclusion. The region has only 100,000 km of fiber optic cable, compared to 1 million km needed for universal coverage. This digital gap costs the region $30 billion annually in lost productivity and innovation.""",
                    
                    'Technical Architecture': """The backbone will use Dense Wavelength Division Multiplexing technology providing 100 Gbps capacity, upgradeable to 400 Gbps. Redundant ring topology will ensure 99.99% uptime. The network will be carrier-neutral, providing open access to all licensed operators. Key routes include Lagos-Abidjan coastal route (1,500 km), Dakar-Bamako-Ouagadougou-Niamey landlocked route (2,500 km), and Accra-Lomé-Cotonou-Lagos coastal route (600 km). Cross-border fiber will use standardized ducts and rights-of-way.""",
                    
                    'Business Model': """The project will operate as a wholesale provider, selling capacity to retail ISPs, mobile operators, and enterprises. Pricing will be regulated to ensure affordability: $500 per Mbps per month for backbone capacity (80% below current prices) and $20 per Mbps per month for last-mile connectivity. Revenue streams include wholesale bandwidth sales ($600 million per year), data center colocation ($150 million per year), and managed services ($100 million per year).""",
                    
                    'Socioeconomic Impact': """Universal broadband access will transform the regional economy: enabling e-government services reaching 100 million citizens, supporting 500,000 digital jobs in software development, BPO, and e-commerce, facilitating $10 billion in digital payments and fintech transactions, improving education through e-learning platforms reaching 5 million students, and enhancing healthcare through telemedicine serving 50 million patients. The digital economy is projected to contribute $50 billion to regional GDP by 2030.""",
                }
            }
        },
    ]
    
    # Generate all documents
    for doc in documents:
        output_path = output_dir / doc['filename']
        create_text_document(output_path, doc['title'], doc['content'])
    
    print()
    print("=" * 60)
    print("✓ Test document generation complete!")
    print("=" * 60)
    print(f"Created {len(documents)} text documents in: {output_dir}")
    print()
    print("Next step: Run ingestion")
    print("  python3 scripts/ingest/batch_ingest.py")


if __name__ == "__main__":
    main()
