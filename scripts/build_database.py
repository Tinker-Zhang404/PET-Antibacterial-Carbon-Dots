from pathlib import Path
import json, csv, re, collections, zipfile
from append_antibacterial import ADDITIONAL_STUDIES, extend_sources, append_records, REVIEW_READING

ROOT=Path.cwd(); OUT=ROOT/'output'/'木质素碳点训练数据库'; OUT.mkdir(parents=True,exist_ok=True)
CSV=OUT/'csv'; CSV.mkdir(exist_ok=True)
manifest=json.loads((ROOT/'tmp/extracted/manifest.json').read_text(encoding='utf-8'))
S=[]; C=[]; P=[]; F=[]; M=[]; R=[]; Q=[]
studies={
'B03':('F01',2024,'Zhu','10.1016/j.biortech.2024.131490','Formation mechanism of lignin-derived carbon quantum dots: From chemical structures to fluorescent behaviors'),
'A02':('F04',2024,'Pan','10.1016/j.cej.2024.155904','Self-adaptive carbon nanozyme regulation of ROS balance for bacteria-infected wound therapy'),
'A01':('F05',2026,'Wang','10.1016/j.cej.2026.175179','Lignin-based carbon quantum dots with adjustable singlet oxygen production for antibacterial application'),
'A03':('F06',2026,'Faria','10.3390/ijms27041945','Two-Step Non-Food Valorization of Phaleria macrocarpa Fruit Lignin into Lignin Nanoparticles and Quantum Dots for Antibacterial and Bioimaging Applications'),
'A04':('F07',2026,'Mohandoss','10.1016/j.diamond.2026.113555','Coconut husk lignin-derived and heteroatom-doped carbon dots as a dual emissive fluorescent probe for ultrasensitive detection of Hg2+ ions with antibacterial and bioimaging applications'),
'A06':('F10',2024,'Rossi','10.1021/acsanm.4c03615','3D-Printed Methacrylated Gelatin-Lignin Carbon Dot Hydrogel Combined with PLA Nanofibers for Wound Dressings'),
'A07':('F12',2025,'Rossi','10.1016/j.mtcomm.2024.111418','Biobased composite fibrous membrane using PLA and lignin carbon dots fabricated via solution blow spinning for wound dressing application'),
'A08':('F14',2025,'Zheng','10.1002/pen.70108','Development of Highly Transparent and Multifunctional Lignin-Derived Carbon Quantum Dots/PVA Composite Films for Active Food Packaging'),
'A05':('F15',2024,'Yang','10.1021/acsanm.3c05880','Thin-Film Composite Polyamide Membranes Decorated with Photoactive Carbon Dots for Antimicrobial Applications')}
studies.update(ADDITIONAL_STUDIES)

def syn(study,label,precursor,temp,time,**kw):
    sid=f'{study}-S{sum(x["study_id"]==study for x in S)+1:02}'
    row=dict(sample_id=sid,study_id=study,sample_label=label,pet_present=0,precursor=precursor,precursor_supplier=None,precursor_fraction=None,method='hydrothermal',temperature_C=temp,time_h=time,water_mL=None,precursor_mass_g=None,precursor_conc_mg_mL=None,precursor_conc_raw=None,additive=None,additive_mass_g=None,additive_volume_mL=None,additive_loading_pct=None,loading_basis=None,additive_precursor_mass_ratio=None,initial_pH=None,reactor_mL=None,sonication_min=None,centrifuge_rpm=None,centrifuge_min=None,filter_um=None,dialysis_MWCO_Da=None,dialysis_h=None,freeze_dry_C=None,freeze_dry_h=None,storage_C=None,source_file_id=studies[study][0],source_locator=None,missing_fields=None,notes=None)
    row.update(kw); S.append(row); return sid

def ingredient(entity,study,name,role,amount=None,unit=None,raw=None,basis=None,stage='CD_synthesis',source=None,loc=None):
    C.append(dict(component_id=f'C{len(C)+1:04}',entity_id=entity,study_id=study,stage=stage,chemical_name=name,role=role,amount=amount,unit=unit,amount_raw=raw,denominator=basis,source_file_id=source or studies[study][0],source_locator=loc,notes=None))

def proc(entity,study,stage,operation,temp=None,time=None,**kw):
    row=dict(process_id=f'P{len(P)+1:04}',entity_id=entity,study_id=study,stage=stage,step_order=sum(x['entity_id']==entity for x in P)+1,operation=operation,temperature_C=temp,duration_h=time,pH=None,volume_mL=None,speed_rpm=None,pressure_bar=None,source_file_id=studies[study][0],source_locator=None,notes=None)
    row.update(kw); P.append(row)

def form(study,label,parent,matrix,**kw):
    fid=f'{study}-F{sum(x["study_id"]==study for x in F)+1:02}'
    row=dict(formulation_id=fid,study_id=study,formulation_label=label,parent_sample_id=parent,matrix=matrix,cd_loading_pct=None,cd_loading_basis=None,cd_mass_mg=None,cd_bath_ug_mL=None,coactive=None,coactive_loading_pct=None,matrix_mass_g=None,processing=None,source_file_id=studies[study][0],source_locator=None,notes=None)
    row.update(kw); F.append(row); return fid

def meas(entity,study,endpoint,value=None,unit=None,loc=None,**kw):
    row=dict(measurement_id=f'M{len(M)+1:04}',entity_id=entity,study_id=study,endpoint=endpoint,value=value,relation='=',value_low=None,value_high=None,uncertainty=None,uncertainty_type=None,unit=unit,value_raw=None,method=None,organism=None,strain=None,gram=None,dose_ug_mL=None,dose_basis=None,disk_mass_ug=None,disk_diameter_mm=None,material_mass_g=None,assay_volume_mL=None,initial_CFU_mL=None,initial_OD600=None,contact_min=None,incubation_h=None,temperature_C=None,medium=None,pH=None,light=None,wavelength_nm=None,wavelength_relation=None,irradiance_mW_cm2=None,lamp_power_W=None,H2O2_mM=None,cofactor=None,control=None,n=None,material_context='free_CD',data_status='reported',regression_eligible=1,evidence_text=None,source_file_id=studies[study][0],source_locator=loc,notes=None)
    row.update(kw)
    if value is None or row['data_status'] in ['conflict','qualitative','figure_only']: row['regression_eligible']=0
    M.append(row); return row

def issue(study,entity,field,problem,handling,source,locator):
    Q.append(dict(issue_id=f'Q{len(Q)+1:03}',study_id=study,entity_id=entity,field=field,issue=problem,handling=handling,source_file_id=source,source_locator=locator))

# B03: fraction-specific samples; the 0.8 g is the first-stage batch, not five hydrothermal charges.
b03=[]
for i,(frac,d,q,y,life,ig,c,o,n) in enumerate(zip(['C1 <=5000 Da','C2 5000-50000 Da','C3 >=50000 Da','C4 0.8-1.2 um','C5 >=1.2 um'],[4.5,4.3,4.1,4.9,5.1],[19.5,18,17.8,.9,3.8],[16.5,9.1,4,.4,1.4],[5.34,5.19,5.09,3.33,3.26],[1.16,1.17,1.14,.98,1.02],[63.14,61.71,59.32,70.14,69.78],[33.55,35.23,37.89,29.68,30.11],[3.31,3.06,2.79,.18,.11]),1):
    sid=syn('B03',f'CQDs-{i}','alkali lignin acidolysis fraction',200,12,precursor_fraction=frac,additive='o-aminobenzenesulfonic acid (pretreatment)',reactor_mL=50,filter_um=.22,dialysis_MWCO_Da=3000,freeze_dry_C=-60,freeze_dry_h=48,source_locator='PDF p2 §§2.2-2.3',missing_fields='各分级组分水热投料质量/水量、透析总时长、初始pH',notes='酸解共同批次为0.8 g AL+0.6 g o-ABSA+30 mL水；不是每个水热样品的投料。')
    b03.append(sid)
    for ep,val,un,loc in [('diameter_TEM_nm',d,'nm','p4 §3.2'),('PLQY_pct',q,'%','p6 Table 3'),('mass_yield_pct',y,'%','p6 Table 3; p2 Eq1'),('PL_lifetime_ns',life,'ns','p6 Table 2'),('Raman_IG_ID',ig,'ratio','p6 §3.3'),('XPS_C_pct',c,'%','p7 Table 4'),('XPS_O_pct',o,'%','p7 Table 4'),('XPS_N_pct',n,'%','p7 Table 4'),('lattice_spacing_nm',.32,'nm','p4 §3.2'),('emission_peak_nm',475 if i<=3 else 400,'nm','p5 §3.2')]:
        meas(sid,'B03',ep,val,un,loc,method='TEM' if ep.startswith('diameter') else None,notes='产率分母为原始AL投料质量。' if ep=='mass_yield_pct' else None)
    proc(sid,'B03','CD_synthesis','hydrothermal carbonization',200,12,source_locator='p2 §2.3')
    proc(sid,'B03','purification','filter 0.22 um PTFE; dialysis MWCO3000; replace water every6h until clear',source_locator='p2 §2.3')
    proc(sid,'B03','drying','freeze-drying',-60,48,source_locator='p2 §2.3')
for chem,role,amt,un in [('alkali lignin','carbon precursor',.8,'g'),('o-aminobenzenesulfonic acid','acid/dopant',.6,'g'),('deionized water','solvent',30,'mL')]: ingredient('B03-PRE','B03',chem,role,amt,un,stage='acidolysis_shared_batch',loc='p2 §2.2')
proc('B03-PRE','B03','pretreatment','acidolysis; stir350 rpm',70,1,speed_rpm=350,volume_mL=30,source_locator='p2 §2.2')
proc('B03-PRE','B03','fractionation','centrifuge; filtration1.2um; MWCO5000/50000; residue filtration0.8um',time=10/60,speed_rpm=8000,source_locator='p2 §2.2')
for entity,mw,mn,pdi,loc in [('B03-AL',5501,2041,2.70,'p4 §3.1.1'),(b03[3],2835,1614,1.75,'p4 §3.1.1 C4 precursor'),(b03[4],3327,1823,1.83,'p4 §3.1.1 C5 precursor')]:
    for ep,val in [('precursor_Mw_g_mol',mw),('precursor_Mn_g_mol',mn),('precursor_PDI',pdi)]: meas(entity,'B03',ep,val,'ratio' if 'PDI' in ep else 'g/mol',loc,material_context='precursor',method='GPC')
issue('B03',b03[2],'PL_lifetime_ns','p5正文将CQDs1-3列成四个寿命值，含5.90；Table2列CQDs3为5.09。','采用明确逐样品Table2=5.09 ns；保留冲突记录。','F01','p5 §3.2; p6 Table2')

# A02: organic acid nanozyme series.
a02=[]
for label,acid in [('LCDs',None),('LCDs-OA','oxalic acid dihydrate'),('LCDs-TA','tartaric acid'),('LCDs-CA','citric acid')]:
    sid=syn('A02',label,'alkali lignin',180,12,precursor_supplier='Macklin',water_mL=20,additive=acid,additive_precursor_mass_ratio=1 if acid else None,loading_basis='equal mass acid:lignin' if acid else None,filter_um=.22,dialysis_MWCO_Da=2000,dialysis_h=48,source_locator='p2 §§2.1-2.2; F08 P26',missing_fields='木质素绝对质量、初始pH、反应釜体积、冻干条件',notes='TA和CA按正文替换等质量OA；酸投料比可知，绝对质量未报告。')
    a02.append(sid); ingredient(sid,'A02','alkali lignin','carbon precursor',raw='mass not stated',loc='p2 §§2.1-2.2'); ingredient(sid,'A02','water','solvent',20,'mL',loc='p2 §§2.1-2.2')
    if acid: ingredient(sid,'A02',acid,'acid / co-carbon source',1,'g/g',raw='same mass as lignin',basis='lignin mass',loc='p2 §2.2')
    proc(sid,'A02','premix','stir',time=.5,source_locator='p2 §§2.1-2.2')
    proc(sid,'A02','CD_synthesis','hydrothermal',180,12,source_locator='p2 §§2.1-2.2')
    proc(sid,'A02','purification','filter0.22um; dialysis2000Da',time=48,source_locator='p2 §§2.1-2.2')
    proc(sid,'A02','drying','freeze-dry; temperature/time not stated',source_locator='p2 §§2.1-2.2')
meas(a02[1],'A02','diameter_TEM_nm',3.9,'nm','p3 §3.1',uncertainty=.4,uncertainty_type='not_specified',n=100,method='TEM')
meas(a02[1],'A02','height_AFM_nm',5.1,'nm','p3 §3.1',uncertainty=1.8,uncertainty_type='not_specified',method='AFM')
meas(a02[1],'A02','lattice_spacing_nm',.22,'nm','p3 §3.1',method='HRTEM')
for sid,vals in [(a02[0],[1.55,3.16,7.81,4.78,11.2,1.01]),(a02[1],[.16,10.92,.49,15.03,.59,2.79])]:
    for ep,val,unit,loc in zip(['POD_Km_TMB_mM','POD_Vmax_TMB_M_s','POD_Km_H2O2_mM','POD_Vmax_H2O2_M_s','CAT_Km_H2O2_mM','CAT_Vmax_O2_mg_L_min'],vals,['mM','M/s','mM','M/s','mM','mg/L/min'],['Supplementary Table2']*4+['Supplementary Table3']*2):
        meas(sid,'A02',ep,val*1e-8 if 'POD_Vmax' in ep else val,unit,loc,source_file_id='F08',method='Michaelis-Menten fit',pH=4.5 if ep.startswith('POD') else 7.4,data_status='unit_converted' if 'POD_Vmax' in ep else 'reported',value_raw=f'{val} (10^-8 M/s)' if 'POD_Vmax' in ep else str(val))
    meas(sid,'A02','Raman_carbonyl_area_pct',.9 if sid==a02[0] else 4.3,'%','Supplementary Table1',source_file_id='F08',method='Raman peak fit')
fcao=form('A02','LCDs-OA@CaO2',a02[1],'CaO2',processing='LCDs-OA:CaO2=1:1; ethanol stirring24h; centrifuge/ethanol wash',source_locator='p2-3 §2.3',notes='CaO2合成段存在明显文字/化学计量异常，未自动纠正。')
ingredient(fcao,'A02','LCDs-OA','CD',1,'part',basis='equal proportion with CaO2; mass basis not explicitly stated',stage='composite',loc='p3 §2.3')
ingredient(fcao,'A02','CaO2','peroxide donor',1,'part',basis='equal proportion with LCDs-OA',stage='composite',loc='p3 §2.3')
proc(fcao,'A02','composite','stir LCDs-OA/CaO2 equal proportions in ethanol',time=24,source_locator='p3 §2.3')
for organism,strain,surv,err in [('Escherichia coli',None,2.6,.1),('Staphylococcus aureus',None,1.3,.2)]:
    meas(a02[1],'A02','bacterial_survival_pct',surv,'%','p9 §3.6; F08 P34',uncertainty=err,uncertainty_type='SD',organism=organism,strain='MDR (strain attribution unresolved)',gram='negative' if 'coli' in organism else 'positive',dose_ug_mL=40,dose_basis='LCDs-OA',initial_OD600=.1,contact_min=240,temperature_C=37,medium='0.1M acetate buffer; subsequent LB',pH=4.5,cofactor='H2O2 present; antibacterial concentration not stated',method='UV-vis bacterial survival',control='acetate buffer',n=3,material_context='free_CD_with_H2O2',notes='不可把酶活测试0.5mM H2O2浓度转移到抗菌试验；MDR与SI购买菌株编号不一致。')
    meas(a02[1],'A02','bacterial_colony_observation',None,None,'p8 §3.6 Fig5',organism=organism,dose_ug_mL=50,contact_min=240,cofactor='H2O2',method='agar colony count observation',data_status='qualitative',material_context='free_CD_with_H2O2',evidence_text='colonies on LB agar plates vanished entirely',notes='无菌落是检出限内观察，不换算100%或MIC。')
for organism,surv,err in [('Escherichia coli',2.1,.2),('Staphylococcus aureus',1.8,.4)]:
    meas(fcao,'A02','bacterial_survival_pct',surv,'%','p9 §3.6; F08 P34',uncertainty=err,uncertainty_type='SD',organism=organism,strain='MDR (strain attribution unresolved)',gram='negative' if 'coli' in organism else 'positive',dose_ug_mL=75,dose_basis='LCDs-OA@CaO2 composite total',initial_OD600=.1,contact_min=240,temperature_C=37,pH=4.5,medium='0.1M acetate buffer',H2O2_mM=0,cofactor='CaO2 supplies peroxide',method='UV-vis bacterial survival',n=3,material_context='CD_CaO2_composite')
issue('A02',a02[1],'strain','正文用MDR E.coli/S.aureus；SI材料列ATCC25922/25923且实验段有E.coli subtilis笔误。','保留物种与MDR原文，不强行赋予ATCC编号。','F04/F08','p8 §3.6; SI P26/P34')
issue('A02',a02[1],'precursor_mass_g','正文未给AL绝对投料量，仅20mL水和酸/AL等质量。','绝对投料留空；不根据同类文献补值。','F04','p2 §§2.1-2.2')

# A01: N-doped photodynamic free CDs.
a01=[]
for i,(lab,loading,qy,so,life) in enumerate(zip(['L-CQDs','N,L-CQDs1','N,L-CQDs2','N,L-CQDs3','N,L-CQDs4'],[None,2,4,6,8],[10.5,12.2,18.1,29.8,22.1],[22.04,45.38,61.56,82.61,45.06],[4.01,4.42,5.40,5.55,5.18])):
    sid=syn('A01',lab,'alkali lignin',200,12,precursor_supplier='Aladdin',water_mL=60,precursor_mass_g=1.2,precursor_conc_mg_mL=20,precursor_conc_raw='1.2g/60mL water',additive='ethylenediamine' if i else None,additive_loading_pct=loading,loading_basis='2/4/6/8 wt%; denominator not specified' if i else None,reactor_mL=100,sonication_min=10,centrifuge_rpm=8000,centrifuge_min=30,filter_um=.22,dialysis_MWCO_Da=500,dialysis_h=32,freeze_dry_h=48,source_locator='p3 §2.2',missing_fields='EDA wt%分母、初始pH、冻干温度（预冻为-80°C）',notes='20mg/mL只以初始水体积计算，非总投料终体积。EDA质量不推算。')
    a01.append(sid)
    ingredient(sid,'A01','alkali lignin','carbon precursor',1.2,'g',loc='p3 §2.2'); ingredient(sid,'A01','water','solvent',60,'mL',loc='p3 §2.2')
    if i: ingredient(sid,'A01','ethylenediamine','nitrogen donor',loading,'wt%',raw=f'{loading} wt%',basis='not specified',loc='p3 §2.2')
    for ep,val,unit,loc in [('PLQY_pct',qy,'%','p6 §3.1 Fig3C'),('singlet_oxygen_QY_pct',so,'%','p6 §3.2'),('PL_lifetime_ns',life,'ns','Table S2')]: meas(sid,'A01',ep,val,unit,loc,source_file_id='F09' if ep=='PL_lifetime_ns' else 'F05',method='quinine sulfate reference' if ep=='PLQY_pct' else ('ABDA; RB reference Phi=0.75' if ep=='singlet_oxygen_QY_pct' else None),irradiance_mW_cm2=100 if ep=='singlet_oxygen_QY_pct' else None,light='xenon' if ep=='singlet_oxygen_QY_pct' else None)
    if i==0: meas(sid,'A01','emission_peak_nm',450,'nm','p6 §3.1')
    meas(sid,'A01','diameter_TEM_nm',[1.60,1.98,1.98,1.99,1.99][i],'nm','p5 Fig1A inset (numeric labels visually verified)',uncertainty=[.58,.59,.69,.58,.73][i],uncertainty_type='not_specified',method='TEM',data_status='reported_figure_label')
    if i<=1: meas(sid,'A01','lattice_spacing_nm',.41 if i==0 else .38,'nm','p4 §3.1; p5 Fig1B',method='HRTEM')
    for stage,op,t,h in [('premix','ultrasonication',None,10/60),('CD_synthesis','hydrothermal',200,12),('purification','centrifuge8000rpm30min; filter0.22um; dialysis500Da32h',None,32),('drying','prefreeze at -80C; freeze-dry48h',None,48)]: proc(sid,'A01',stage,op,t,h,source_locator='p3 §2.2')
for sid,c,n,o in zip(a01,[76.61,74.25,72.22,64.07,64.00],[0,4.88,7.61,8.94,8.98],[23.39,20.87,19.84,23.67,23.64]):
    total=c+n+o; status='reported' if abs(total-100)<=.1 else 'conflict'
    for ep,val in [('XPS_C_pct',c),('XPS_N_pct',n),('XPS_O_pct',o)]: meas(sid,'A01',ep,val,'%','Table S1',source_file_id='F09',method='XPS',data_status=status,notes=f'C+N+O={total:.2f}%; inconsistent total retained' if status=='conflict' else None)
    if status=='conflict': issue('A01',sid,'XPS_C_N_O_pct',f'SI TableS1 C+N+O合计{total:.2f}%，偏离100%。','保留原值、标conflict，默认不作回归标签；不归一化为100%。','F09','Table S1')
for org,val in [('Staphylococcus aureus',99.57),('Escherichia coli',93.60)]:
    meas(a01[3],'A01','bacterial_inhibition_pct',val,'%','p7 §3.3; F09 FigS5',organism=org,gram='positive' if 'aureus' in org else 'negative',dose_ug_mL=30,dose_basis='CD',contact_min=15,incubation_h=24,light='xenon',irradiance_mW_cm2=100,method='plate colony count',evidence_text='optimized concentration30ug/mL inhibition99.57% S.aureus and93.60% E.coli',notes='FigS5与Fig5时间实验存在数值差异，作为不同试验保留。')
for org,t in [('Staphylococcus aureus',15),('Escherichia coli',20)]:
    meas(a01[3],'A01','bacterial_survival_pct',0,'%','p7 §3.3; p8 Fig5A-B',organism=org,gram='positive' if 'aureus' in org else 'negative',dose_ug_mL=30,dose_basis='CD',contact_min=t,incubation_h=24,light='xenon',irradiance_mW_cm2=100,method='plate colony count',relation='reported_zero',regression_eligible=0,evidence_text='survival rate decreases to0; complete inhibition',notes='检出限未给；零存活不等于无限log杀菌率；剂量来自优化实验语境。')
issue('A01',a01[3],'bacterial_inhibition_pct','同15min语境下浓度筛选报告S.aureus99.57%，时间曲线正文报告0存活。','分试验记录，先不合并平均；训练时择一致协议。','F05/F09','p7 §3.4; Fig5; FigS5')
issue('A01','A01-all','additive_loading_pct','EDA仅给2/4/6/8wt%，未定义按水、溶液还是木质素作分母。','保留原始百分数和unknown denominator；不换算g或g/g。','F05','p3 §2.2')
fa01=form('A01','PVA/HA/N,L-CQDs3 optimal patch',a01[3],'PVA + sodium hyaluronate',cd_mass_mg=30,matrix_mass_g=5,processing='PVA5g/25mL water90C1h; HA0.5g/25mL water30min; mix; five freeze-thaw cycles(-20C8h/cycle)',source_locator='p4 §2.5; p8 §3.4',notes='30mg为每批加入量，不能当作局部创面给药剂量；HA分子量<=40000。')
for name,role,am,un in [('PVA','matrix',5,'g'),('sodium hyaluronate','matrix',.5,'g'),('N,L-CQDs3','CD',30,'mg'),('water','solvent',50,'mL')]: ingredient(fa01,'A01',name,role,am,un,stage='hydrogel',loc='p4 §2.5')
proc(fa01,'A01','matrix','PVA dissolve in25mL water',90,1,source_locator='p4 §2.5')
proc(fa01,'A01','crosslink','five freeze-thaw cycles: freeze -20C8h each; complete room-temperature thaw',-20,8,source_locator='p4 §2.5',notes='8h为每周期冻结时间；5cycles，不是总耗时。')

# A03 green free lignin quantum dots.
a03=syn('A03','LQDs','Phaleria macrocarpa fruit lignin nanoparticles',180,12,precursor_conc_mg_mL=1000/30,precursor_conc_raw='LNP:water=1:30 g:mL',centrifuge_rpm=10000,centrifuge_min=15,filter_um=.2,freeze_dry_C=-40,freeze_dry_h=48,storage_C=4,source_locator='p16-17 §3.2.2',missing_fields='绝对投料、初始pH、反应釜容量',notes='无外加催化剂；未报告透析，不记为透析0h。')
ingredient(a03,'A03','LNP','carbon precursor',1,'g',raw='1:30 g:mL; ratio basis only',basis='ratio basis, not absolute charge',loc='p16 §3.2.2'); ingredient(a03,'A03','water','solvent',30,'mL',raw='1:30 g:mL; ratio basis only',basis='ratio basis, not absolute volume',loc='p16 §3.2.2')
proc('A03-PRE','A03','extraction','4%w/v NaOH; fruit:liquid1:20g:mL; stir400rpm',90,6,speed_rpm=400,source_locator='p16 §3.2.1')
proc('A03-PRE','A03','precipitation','30%w/w H2SO4 dropwise in ice bath',pH=.5,source_locator='p16 §3.2.1')
proc('A03-PRE','A03','washing','centrifuge10000rpm15min; wash to neutral; ultrasound15min; freeze-dry',speed_rpm=10000,source_locator='p16 §3.2.1')
proc(a03,'A03','CD_synthesis','hydrothermal',180,12,source_locator='p16 §3.2.2')
proc(a03,'A03','purification','Whatman40; centrifuge10000rpm15min; filter0.2um',source_locator='p16 §3.2.2')
proc(a03,'A03','drying','freeze-dry',-40,48,source_locator='p17 §3.2.2')
for ep,val,unit,loc in [('PLQY_pct',5.33,'%','p11 §2.3'),('PL_lifetime_ns',4.51,'ns','p11 §2.3'),('emission_peak_nm',490,'nm','p11 §2.3'),('absorption_peak_nm',288,'nm','p1 abstract')]: meas(a03,'A03',ep,val,unit,loc)
meas(a03,'A03','diameter_TEM_nm',None,'nm','p12 Table2',relation='range',value_low=3,value_high=5,data_status='reported_range')
for org,gram,vals in [('Staphylococcus aureus','positive',[(24,21.77,.57),(72,29.23,.54)]),('Klebsiella pneumoniae','negative',[(24,20.27,1.30),(72,19.54,.38)])]:
    for h,val,sd in vals: meas(a03,'A03','zone_of_inhibition_mm',val,'mm','p10 Table1; p17 methods',uncertainty=sd,uncertainty_type='SD',organism=org,gram=gram,disk_mass_ug=50,disk_diameter_mm=6,initial_CFU_mL=1.5e8,incubation_h=h,temperature_C=37,medium='Mueller-Hinton agar',method='disk diffusion',n=3,control='solvent negative; erythromycin15ug positive',notes='原文ZOI未明确是否包含纸片直径，保留原值且不扣6mm；对照部分ZOI小于纸片直径，定义需核查。')
meas(a03,'A03','cell_viability_pct',93.1,'%','p10 §2.2.2; p18 methods',uncertainty=6.5,uncertainty_type='SD',organism='L929 mouse fibroblast',dose_ug_mL=50,incubation_h=24,temperature_C=37,method='MTT')
issue('A03',a03,'bioimaging_dose','讨论称与L929试验相同浓度，方法里成像为500ug/mL而细胞毒性50ug/mL。','生物相容性仅绑定50ug/mL、24h；不外推到500ug/mL。','F06','p14 discussion; p18 methods')
issue('A03',a03,'zone_of_inhibition_mm','使用6mm纸片；阳性对照K.pneumoniae的ZOI4.42/2.50mm小于纸片，是否包含纸片直径定义不清。','不定义为含纸片总径或净径，保留ZOI原值与纸片尺寸；跨论文建模前确认定义。','F06','p10 Table1; p17 methods')

# A04: precursor described as coconut husk carbon; concentration conflict in antibacterial section.
a04=syn('A04','Lig-NCDs','coconut husk carbon (authors call lignin-derived)',180,12,precursor_mass_g=.020,additive='o-phenylenediamine',additive_mass_g=.050,additive_precursor_mass_ratio=2.5,filter_um=.22,dialysis_h=24,storage_C=4,source_locator='p2 §§2.2-2.3',missing_fields='水体积、透析MWCO、超声时间、初始pH、原料木质素纯度',notes='摘要称lignin-derived，方法实际写coconut husk carbon；碱处理后原料纯度未定量。2.5g/g由50/20mg计算。')
for chem,role,amt in [('coconut husk carbon','carbon precursor',20),('o-phenylenediamine','nitrogen donor',50)]: ingredient(a04,'A04',chem,role,amt,'mg',loc='p2 §2.3')
proc('A04-PRE','A04','pretreatment','30mg dried coconut husk;2%NaOH; wash untilpH7',120,4,source_locator='p2 §2.2',notes='NaOH体积未给；原文30mg量值按原文保留。')
proc('A04-PRE','A04','drying','oven drying',70,None,source_locator='p2 §2.2')
proc(a04,'A04','premix','aqueous dispersion20min then add50mg o-PDA and sonicate',time=20/60,source_locator='p2 §2.3')
proc(a04,'A04','CD_synthesis','hydrothermal',180,12,source_locator='p2 §2.3')
proc(a04,'A04','cooling','cool',time=12,source_locator='p2 §2.3')
proc(a04,'A04','purification','filter0.22um; dialysis24h',time=24,source_locator='p2 §2.3')
meas(a04,'A04','diameter_TEM_nm',3.87,'nm','p7 §3.3 Fig2e',uncertainty=.12,uncertainty_type='not_specified',method='TEM')
meas(a04,'A04','PLQY_pct',35.23,'%','p5 §3.1',method='quinine sulfate reference (54%)')
meas(a04,'A04','lattice_spacing_nm',.21,'nm','p7 §3.3',method='HRTEM')
for org in ['Staphylococcus aureus','Escherichia coli']:
    meas(a04,'A04','bacterial_colony_reduction_pct',None,'%','p10 §3.5; p4 §2.9',relation='range',value_low=15,value_high=20,value_raw='5 mg/mL; slight reduction15-20%',data_status='conflict',organism=org,contact_min=240,incubation_h=24,temperature_C=None,medium='LB',method='plate colony count',dose_basis='results:5mg/mL; methods:5,10,20ug/mL',notes='范围未分别分配给物种，菌初浓度原文1x10^-6CFU/mL疑错。')
fhg=form('A04','Lig-NCDs/Hg2+',a04,'none',coactive='Hg2+',processing='pre-coordinate Lig-NCDs with Hg2+',source_locator='p10 §3.5',notes='重金属本身毒性贡献；不作为PET安全搭配材料的候选证据。')
for org in ['Staphylococcus aureus','Escherichia coli']: meas(fhg,'A04','bacterial_colony_reduction_pct',None,'%','p10 §3.5',relation='range',value_low=70,value_high=80,value_raw='Hg2+5-10uM; reduction70-80%',data_status='conflict',organism=org,cofactor='Hg2+5-10uM',contact_min=240,incubation_h=24,method='plate colony count',material_context='CD_Hg_complex',notes='不能分配Hg具体浓度与菌种；排除PET候选路线。')
issue('A04',a04,'dose_ug_mL / initial_CFU_mL','方法剂量5/10/20ug/mL，结果为5mg/mL；初始菌量写1x10^-6CFU/mL。','不改为猜测值；剂量/菌量标准列留空，抗菌数值默认排除回归。','F07','p4 §2.9; p10 §3.5')

# A06: hydrogel precursors and bilayer products are separate assay entities.
a06=syn('A06','lignin CDs','Kraft lignin',180,5.5,precursor_supplier='Ingevity',precursor_mass_g=1.05,water_mL=35,precursor_conc_mg_mL=30,precursor_conc_raw='1.05g/35mL water',centrifuge_rpm=8000,centrifuge_min=20,filter_um=.22,dialysis_MWCO_Da=2000,dialysis_h=48,storage_C=8,source_locator='p3 §2.2',missing_fields='初始pH、反应釜容量、碳点QY/粒径定量值')
ingredient(a06,'A06','Kraft lignin','carbon precursor',1.05,'g',loc='p3 §2.2'); ingredient(a06,'A06','water','solvent',35,'mL',loc='p3 §2.2')
proc(a06,'A06','CD_synthesis','hydrothermal',180,5.5,source_locator='p3 §2.2'); proc(a06,'A06','purification','centrifuge8000rpm20min; filter0.22um; dialysis2000Da48h',time=48,source_locator='p3 §2.2')
proc('A06-GMA','A06','matrix_synthesis','10g gelatin/100mL PBS pH7.4;6mL methacrylic anhydride',50,3,pH=7.4,source_locator='p3 §2.2')
proc('A06-GMA','A06','matrix_purification','dilute with300mL PBS; dialysis12-14kDa7days; freeze -20C; lyophilize7days',time=168,source_locator='p3 §2.2',notes='7days透析与7days冻干为两个步骤。')
af06=[]; bf06=[]
for load in [0,5,10]:
    ff=form('A06','GMA' if load==0 else f'GMA/CD{load}',a06 if load else None,'methacrylated gelatin+gelatin',cd_loading_pct=load,cd_loading_basis='reported wt%; denominator not explicitly specified',processing='50mg Irgacure2959/5mL PBS;0.5g GMA; mix with0.3g gelatin solution1:1v/v',source_locator='p3 §2.3',notes='抗菌测试用水凝胶前驱液；不是最终PLA复合膜。')
    af06.append(ff)
    ingredient(ff,'A06','GMA','matrix',.5,'g',stage='hydrogel',loc='p3 §2.3'); ingredient(ff,'A06','gelatin','matrix',.3,'g',stage='hydrogel',loc='p3 §2.3'); ingredient(ff,'A06','Irgacure2959','photoinitiator',50,'mg',stage='hydrogel',loc='p3 §2.3')
    if load: ingredient(ff,'A06','CD','filler',load,'wt%',basis='denominator not explicit',stage='hydrogel',loc='p3 §2.3')
    final=form('A06','PLA/GMA' if load==0 else f'PLA/GMA/CD{load}',a06 if load else None,'PLA + GMA hydrogel',cd_loading_pct=load,cd_loading_basis='hydrogel formulation reported wt%',processing='PLA12%w/v CHCl3/DMF4:1; SBS7.5mL/h2bar22cm;3D-print30x22x0.5mm; UV365nm30min',source_locator='p3 §2.3',notes='printing speed原文3.3m/s，未擅自改单位；前驱水凝胶关联'+ff)
    bf06.append(final)
    proc(final,'A06','PLA_SBS','12%w/v PLA;CHCl3/DMF4:1; premix15h; flow7.5mL/h;2bar;22cm; RH35%; collector180rpm',25,None,pressure_bar=2,source_locator='p3 §2.3')
    proc(final,'A06','crosslink','UV365nm; cabinet15W',time=.5,source_locator='p3 §2.3')
    for org,strain in [('Staphylococcus aureus','ATCC25923'),('Escherichia coli','ATCC25922')]:
        meas(ff,'A06','contact_growth_inhibition',1 if load else 0,'binary','p9 §3.7 Fig6A-B; p4 §2.11',organism=org,strain=strain,disk_diameter_mm=5,initial_CFU_mL=1e8,incubation_h=24,temperature_C=37,medium='Mueller-Hinton agar',method='disk diffusion contact observation',material_context='hydrogel_precursor',data_status='qualitative',value_raw='growth inhibited upon contact' if load else 'pure GMA excluded from contact inhibition',notes='25uL前驱水凝胶/纸片；无抑菌圈不等于无接触抑菌活性。')
        meas(ff,'A06','zone_observation',None,None,'p9 §3.7 Fig6A-B',organism=org,incubation_h=24,method='disk diffusion',material_context='hydrogel_precursor',data_status='qualitative',evidence_text='no zones of inhibition observed around filters',notes='未报告外圈数值，不填0mm。')
    for h,red in [(24,[1.8,2.53,9.02][[0,5,10].index(load)]),(48,[5.32,1.48,4.97][[0,5,10].index(load)])]: meas(final,'A06','cell_viability_reduction_pct',red,'%','p10 §3.8',relation='approximately',organism='HDFn human dermal fibroblast',incubation_h=h,method='MTT extract assay',material_context='PLA_GMA_bilayer',notes='保留原文下降率；不当作杀菌率。')

# A07: PLA/curcumin composites.
a07=syn('A07','LCdots','Kraft lignin',180,5.5,precursor_supplier='Ingevity',precursor_conc_raw='2.5 wt% aqueous lignin',filter_um=.22,dialysis_MWCO_Da=2000,dialysis_h=48,source_locator='p3 §2.2',missing_fields='绝对质量、水体积、初始pH、碳点QY',notes='2.5wt%未按溶液密度换算mg/mL。-45C48h仅用于小份冻干测浓度。')
ingredient(a07,'A07','Kraft lignin','carbon precursor',2.5,'wt%',basis='aqueous solution',loc='p3 §2.2')
proc(a07,'A07','CD_synthesis','hydrothermal;2.5wt% aqueous lignin',180,5.5,source_locator='p3 §2.2'); proc(a07,'A07','purification','filter0.22um;dialysis2000Da48h',time=48,source_locator='p3 §2.2')
meas(a07,'A07','diameter_TEM_nm',2.4,'nm','p4 §3.1 Fig2B',uncertainty=.5,uncertainty_type='not_specified',method='TEM')
meas(a07,'A07','suspension_CD_mg_g',14,'mg/g','p3 §2.2',uncertainty=.8,uncertainty_type='not_specified',notes='悬浮液浓度，不是碳点合成产率。')
meas(a07,'A07','emission_peak_nm',390,'nm','p4 §3.1',relation='approximately',wavelength_nm=300,method='PL excitation300nm')
af07=[]
for label,load,cur,diam,sd,visc in [('PLA',0,0,619,17,68),('PLA/LCdots',2,0,551,18,65),('PLA/Cur',0,10,468,17,57),('PLA/LCdots/Cur',2,10,512,19,52)]:
    ff=form('A07',label,a07 if load else None,'PLA',cd_loading_pct=load,cd_loading_basis='PLA mass',coactive='curcumin' if cur else None,coactive_loading_pct=cur,processing='PLA12%w/v CHCl3/DMF4:1;stir15h;SBS2bar22cm',source_locator='p3 §2.3',notes='SBS优化参数TableS1未在本地提供。')
    af07.append(ff)
    ingredient(ff,'A07','PLA','matrix',12,'%w/v',basis='polymer solution',stage='SBS',loc='p3 §2.3')
    if load: ingredient(ff,'A07','LCdots','CD',2,'wt%',basis='PLA mass',stage='SBS',loc='p3 §2.3')
    if cur: ingredient(ff,'A07','curcumin','co-antibacterial agent',10,'wt%',basis='PLA mass',stage='SBS',loc='p3 §2.3')
    proc(ff,'A07','SBS','CHCl3/DMF4:1;12%w/v PLA;2bar;22cm;nozzle0.5mm',pressure_bar=2,source_locator='p3 §2.3')
    meas(ff,'A07','fiber_diameter_SEM_nm',diam,'nm','p6 §3.2',uncertainty=sd,uncertainty_type='not_specified',method='SEM',material_context='PLA_fibrous_mat')
    meas(ff,'A07','solution_viscosity_cP',visc,'cP','p6 §3.2',material_context='SBS_solution')
    for org,strain in [('Staphylococcus aureus','ATCC25923'),('Pseudomonas aeruginosa','ATCC27853')]:
        meas(ff,'A07','contact_growth_inhibition',0 if not(load or cur) else 1,'binary','p7 §3.4.1; p4 §2.7',organism=org,strain=strain,initial_CFU_mL=1e8,incubation_h=24,temperature_C=37,medium='Mueller-Hinton agar',method='disk diffusion contact observation',material_context='PLA_fibrous_mat',data_status='qualitative',value_raw='no contact inhibition' if not(load or cur) else 'contact growth inhibited')
        meas(ff,'A07','zone_observation',None,None,'p7 §3.4.1',organism=org,method='disk diffusion',material_context='PLA_fibrous_mat',data_status='qualitative',evidence_text='no inhibition zones observed around specimens',notes='不赋值0mm。')
    meas(ff,'A07','microbial_penetration_growth',0,'binary','p8 §3.4.2; p4 §2.7',incubation_h=240,medium='MHB15mL; air exposure',method='microbial penetration',material_context='PLA_fibrous_mat',data_status='qualitative',value_raw='no turbidity / no microbial growth',notes='所有PLA膜包括纯PLA均为屏障阴性，不能视为游离碳点杀菌证据。')
for ff,ep,val,sd in [(af07[1],'CD_encapsulation_pct',77.6,5),(af07[2],'curcumin_encapsulation_pct',74.2,3),(af07[3],'CD_encapsulation_pct',58.8,1),(af07[3],'curcumin_encapsulation_pct',72,1)]: meas(ff,'A07',ep,val,'%','p7 Table1',uncertainty=sd,uncertainty_type='not_specified',material_context='PLA_fibrous_mat')

# A08: precise dose/time/light distinctions retained.
a08=syn('A08','LCQDs','enzymatic hydrolysis lignin',220,12,precursor_mass_g=1,water_mL=20,precursor_conc_mg_mL=50,precursor_conc_raw='1g/20mL water',additive='citric acid',additive_mass_g=.8,additive_precursor_mass_ratio=.8,sonication_min=30,filter_um=.22,freeze_dry_C=-60,freeze_dry_h=72,source_locator='p2 §2.2',missing_fields='初始pH、反应釜容量、透析（未报告）',notes='预冻-20C12h；冻干压力原文20MPa疑错，未标准化。')
for name,role,am,un in [('enzymatic lignin','carbon precursor',1,'g'),('citric acid','acid/co-carbon source',.8,'g'),('water','solvent',20,'mL')]: ingredient(a08,'A08',name,role,am,un,loc='p2 §2.2')
proc('A08-PRE','A08','extraction','4wt%NaOH; solid/liquid1:15; repeated stirring/centrifugation; neutral precipitate; dry/grind',source_locator='p2 §2.1',notes='中和方法/时间温度未给。')
proc(a08,'A08','premix','sonication',time=.5,source_locator='p2 §2.2'); proc(a08,'A08','CD_synthesis','hydrothermal',220,12,source_locator='p2 §2.2'); proc(a08,'A08','drying','prefreeze -20C12h then lyophilize -60C72h',-60,72,source_locator='p2 §2.2')
meas(a08,'A08','diameter_TEM_nm',2.4,'nm','p4 §3.1',method='TEM'); meas(a08,'A08','lattice_spacing_nm',.21,'nm','p4 §3.1',method='HRTEM')
af08=[]
for load in [0,5,10,20]:
    ff=form('A08','PVA' if load==0 else f'PVA-{load}%LCQDs',a08 if load else None,'PVA1750',cd_loading_pct=load,cd_loading_basis='reported mass%; denominator not explicitly defined',matrix_mass_g=5,processing='PVA5g/100mLwater90C4h;addCD80C30min;cast20x20cm;dry25C48h;condition25C50%RH48h',source_locator='p2 §2.3')
    af08.append(ff); ingredient(ff,'A08','PVA1750','matrix',5,'g',stage='film',loc='p2 §2.3'); ingredient(ff,'A08','water','solvent',100,'mL',stage='film',loc='p2 §2.3')
    if load: ingredient(ff,'A08','LCQDs','CD',load,'wt%',basis='not explicitly defined',stage='film',loc='p2 §2.3')
    proc(ff,'A08','film','PVA dissolve',90,4,source_locator='p2 §2.3'); proc(ff,'A08','mix','add LCQDs and stir',80,.5,source_locator='p2 §2.3'); proc(ff,'A08','drying','cast20x20cm PTFE mold; dry',25,48,source_locator='p2 §2.3'); proc(ff,'A08','conditioning','50% RH',25,48,source_locator='p2 §2.3')
def a08test(ff,org,ep,val,t,light,loc):
    return meas(ff,'A08',ep,val,'%',loc,organism=org,gram='negative' if 'coli' in org else 'positive',material_mass_g=.1,assay_volume_mL=10,initial_CFU_mL=1e6,contact_min=t,incubation_h=24,medium='0.85wt% saline; PCA plating',light=light,wavelength_nm=420 if light=='visible' else None,wavelength_relation='>' if light=='visible' else None,lamp_power_W=300 if light=='visible' else None,method='plate colony count',control='untreated sample',n=3,material_context='PVA_film',notes='方法称每10min取样，结果正文以15/45min报告；保留结果明确时间。')
for idx,ff in enumerate(af08[1:]):
    for t,light,vals in [(15,'dark',[47.45,46,29.45]),(45,'dark',[29.09,4.18,0]),(15,'visible',[27.27,12.9,6])]: a08test(ff,'Escherichia coli','bacterial_survival_pct',vals[idx],t,light,'p8 §3.5')
    for light,vals in [('dark',[23.22,25.5,31.47]),('visible',[34.31,48.53,88.44])]: a08test(ff,'Staphylococcus aureus','bacterial_killing_pct',vals[idx],45,light,'p9 §3.5')
for ff in af08[2:]: a08test(ff,'Escherichia coli','bacterial_killing_pct',100,45,'visible','p8 §3.5')
issue('A08','A08-all','contact_min','方法每10min取样，结果用15/45min；结论提E.coli30min达100%，正文明确45min。','保留正文明确样品对应的15/45min；结论30min不分配到特定配方。','F14','p4 methods;p8-9 results/conclusions')
issue('A08',a08,'freeze_dry_pressure','冻干压力原文20MPa，明显不符合常规真空冻干表述。','只保留原文注释，不把20MPa当作可执行实验参数。','F14','p2 §2.2')

# A05 photoactive membrane; CD preparation10min is deliberately not changed to10h.
a05=syn('A05','CD','elephant grass leaf lignin (Pennisetum purpureum)',180,10/60,precursor_mass_g=.1,water_mL=30,precursor_conc_mg_mL=100/30,precursor_conc_raw='100mg lignin/30mLwater +2mL H2O2 solution',additive='hydrogen peroxide30%',additive_volume_mL=2,loading_basis='30% H2O2 stock; concentration basis not specified',sonication_min=45,filter_um=.22,dialysis_MWCO_Da=3500,dialysis_h=24,storage_C=4,source_locator='p3 Preparation of Carbon Dots',missing_fields='初始pH、反应釜容量、H2O2百分浓度基准',notes='水热时间明确10min=0.166667h；3.333mg/mL只按30mL水，不含H2O2溶液体积。')
for name,role,am,un in [('lignin','carbon precursor',100,'mg'),('water','solvent',30,'mL'),('H2O2 30% stock','oxidant',2,'mL')]: ingredient(a05,'A05',name,role,am,un,loc='p3 Preparation of Carbon Dots')
proc('A05-PRE','A05','extraction','1%v/vH2SO4;solid/liquid1:10;1.05bar',121,40/60,pressure_bar=1.05,source_locator='p3 Preparation of Carbon Dots')
proc('A05-PRE','A05','extraction','2%w/vNaOH;solid/liquid1:20;1.05bar',121,40/60,pressure_bar=1.05,source_locator='p3 Preparation of Carbon Dots')
proc('A05-PRE','A05','precipitation','concH2SO4;filter;wash until pH6-7;dry40C12h',40,12,source_locator='p3 Preparation of Carbon Dots')
proc(a05,'A05','premix','bath sonication',time=.75,source_locator='p3 Preparation of Carbon Dots'); proc(a05,'A05','CD_synthesis','H2O2 assisted hydrothermal',180,10/60,source_locator='p3 Preparation of Carbon Dots'); proc(a05,'A05','purification','0.22umPVDF;dialysis3500Da24h',time=24,source_locator='p3 Preparation of Carbon Dots')
for ep,val,unit in [('diameter_TEM_nm',10.7,'nm'),('PLQY_pct',47.8,'%'),('emission_peak_nm',470,'nm'),('excitation_peak_nm',380,'nm'),('XPS_C_pct',61.9,'%'),('XPS_O_pct',34.4,'%'),('XPS_S_pct',2.1,'%'),('XPS_Ca_pct',1.7,'%')]: meas(a05,'A05',ep,val,unit,'p6 CD characterization; Fig2',uncertainty=1.9 if ep=='diameter_TEM_nm' else None,uncertainty_type='not_specified' if ep=='diameter_TEM_nm' else None,n=62 if ep=='diameter_TEM_nm' else None)
af05={}
for label,conc in [('TFC',None),('TFC-PDA',None),('CD-100',100),('CD-300',300),('CD-500',500),('CD-1000',1000)]:
    ff=form('A05',label,a05 if conc else None,'TFC polyamide membrane + PDA' if label!='TFC' else 'TFC polyamide membrane',cd_bath_ug_mL=conc,processing='dopamine50mg/25mL10mMTris pH8.5 15min; CD bath24h atRT30rpm;rinse;store4C' if label!='TFC' else 'commercial FilmTec SW30XLE',source_locator='p3 Membrane Functionalization',notes='浓度为表面修饰浴浓度，不是实测膜负载量或测试液游离CD剂量。')
    af05[label]=ff
    if label!='TFC': proc(ff,'A05','coating','dopamine50mg/25mL10mMTris; pH8.5;15min;30rpm',time=.25,pH=8.5,speed_rpm=30,source_locator='p3 Membrane Functionalization')
    if conc: proc(ff,'A05','CD_coating',f'CD bath{conc}ug/mL;10mMTris;pH8.5',time=24,pH=8.5,source_locator='p3 Membrane Functionalization')
rows05=[('CD-100','Escherichia coli','dark',20.6,1.04),('CD-1000','Escherichia coli','dark',74.2,.62),('CD-100','Bacillus subtilis','dark',27.9,3),('CD-1000','Bacillus subtilis','dark',73.4,1.8),('TFC','Escherichia coli','daylight',62.2,2.5),('TFC','Bacillus subtilis','daylight',73,2.6),('CD-100','Escherichia coli','daylight',67.9,4.9),('CD-1000','Escherichia coli','daylight',81.1,.9),('CD-100','Bacillus subtilis','daylight',75.6,.5),('CD-1000','Bacillus subtilis','daylight',87.3,2.6),('TFC','Escherichia coli','UV',97.9,.15),('TFC','Bacillus subtilis','UV',99.87,.017),('CD-1000','Escherichia coli','UV',99.97,.045),('CD-500','Escherichia coli','dark',69.9,1.7),('CD-500','Escherichia coli','daylight',76.4,1.8),('CD-500','Escherichia coli','UV',99.92,.03)]
for label,org,light,val,sd in rows05:
    meas(af05[label],'A05','bacterial_inactivation_pct',val,'%','p8 Fig5/results; p1 abstract forCD500; p4-5 methods',uncertainty=sd,uncertainty_type='not_specified',organism=org,strain='ATCC8739' if 'coli' in org else 'ATCC6633',gram='negative' if 'coli' in org else 'positive',assay_volume_mL=5,initial_CFU_mL=1e8,contact_min=180,medium='0.85%NaCl saline',light=light,wavelength_nm=365 if light=='UV' else None,lamp_power_W=3 if light=='UV' else 3.5 if light=='daylight' else None,method='attached bacterial plate count',control='pristineTFC in darkness',n=4,material_context='TFC_PDA_membrane',notes='daylight为3500K LED；灯额定W不能换算样品处mW/cm2。测试为附着细菌相对TFC暗对照。')
meas(af05['CD-500'],'A05','bacterial_inactivation_pct',71.4,'%','p11 Fig8; p1 abstract',uncertainty=.6,uncertainty_type='not_specified',organism='Escherichia coli',strain='ATCC8739',contact_min=180,medium='synthetic wastewater',light='UV',wavelength_nm=365,lamp_power_W=3,method='attached bacterial plate count',control='TFC in darkness',n=4,material_context='TFC_PDA_membrane')

# Correct subsection locators after checking the PDF page text.
for row in M:
    if row['study_id']=='A02' and row['source_locator']:
        row['source_locator']=row['source_locator'].replace('§3.6','§3.5')
    if row['study_id']=='A02' and row['endpoint']=='bacterial_survival_pct':
        row['n']=None; row['uncertainty_type']='not_specified'
    if row['endpoint']=='bacterial_survival_pct' and row['value']==0:
        row['relation']='reported_zero'; row['regression_eligible']=0
    if row['study_id']=='A05' and row['endpoint']=='emission_peak_nm':
        row['relation']='approximately'
for row in Q:
    if row['study_id']=='A02': row['source_locator']=row['source_locator'].replace('§3.6','§3.5')
    if row['study_id']=='A01': row['source_locator']=row['source_locator'].replace('§3.4','§3.3')

# Review evidence is kept in a separate collection, never silently joined into primary training.
def secondary(file,ref,precursor,agent,condition,qy=None,size=None,em=None,ratio=None,yield_raw=None,note=None):
    R.append(dict(secondary_id=f'R{len(R)+1:03}',source_file_id=file,source_locator='p8 Table3' if file=='F19' else 'p4 Table1' if file=='F20' else 'p9 Table3',original_reference=ref,precursor=precursor,additive=agent,conditions_raw=condition,PLQY_pct=qy,diameter_raw_nm=size,emission_raw_nm=em,ratio_raw=ratio,yield_raw_pct=yield_raw,source_level='secondary_review',include_primary_training=0,notes=note or '需追溯原始论文；不同综述/本地全文可能重复，不计独立样本。'))
review19=[
('[16]','alkali lignin','N','1.0/7.6',9.2,'86'),('[32]','softwood alkali lignin','N,S','1.0/1.0',30.5,None),('[36]','sodium lignosulfonate','S',None,None,'29.5'),('[37]','grass EHL','N','1.0/24/21',43.9,None),('[38]','hardwood DES lignin','N','1.0/3.0',22,None),('[39]','lignin',None,None,None,'2.3'),('[44]','hardwood alkali lignin','N','1/22/70',43,None),('[45]','alkali lignin','N','1.0/5.4',17.6,'82.4'),('[57]','hardwood alkali lignin','N,S','1.0/1.0',20.6,None),('[97]','corncob bioethanol residue lignin','N',None,42.7,'68'),('[97]','softwood alkali lignin','N,S','1.0/1.0',None,'15.2-30.6'),('[110]','grass EHL','N,S',None,45,None),('[111]','grass ethanol-water lignin','N,Mg','1.0/0.4/0.2',46.4,None),('[93]','hardwood alkali lignin','N,S','1.0/1.0',21,'18'),('[145]','softwood alkali lignin',None,None,13,'6.0-7.0'),('[146]','sodium lignosulfonate','S','1.5/1.0',47.3,'5.0'),('[157]','sodium lignosulfonate','K,Cl','1.0/1.0',15,None),('[79]','grass alkali lignin',None,None,None,'18'),('[81]','softwood alkali lignin',None,None,21,'21'),('[99]','softwood alkali lignin','N','1.0/2.5',22.2,'39.28'),('[104]','coconut husk lignin','N','1.0/330',6,'40'),('[115]','softwood alkali lignin','N,S','1.0/1.0',23.7,None),('[85]','softwood alkali lignin','N',None,28,None),('[121]','softwood alkali lignin','MCC','1.0/1.0',23.4,None),('[89]','sodium lignosulfonate','N,S,Mn','1.0/0.01',31.6,None),('[122]','softwood alkali lignin','N','1.0/6.7/10',33.2,None),('[158]','softwood alkali lignin','N','1.0/3.0',37.3,None),('[92]','softwood alkali lignin','N','1.0/3.0',41.5,None),('[83]','hardwood hydrolyzed lignin','N','1.0/10.8',42.7,None),('[148]','softwood alkali lignin','Cd,S','1.0/1.0/0.55/0.1',66,None)]
for ref,pre,agent,ratio,qy,y in review19: secondary('F19',ref,pre,agent,'Table3 does not provide synthesis temperature/time',qy,ratio=ratio,yield_raw=y,note='QY原表范围5.2-23.7%（本行点值留空）。' if ref=='[97]' and qy is None else 'QY原表8.0-9.0%（本行点值留空）。' if ref=='[79]' else None)
for ref,agent,q,em in [('[44]','ammonia',8.2,452),('[28]','ethylenediamine',17.6,525),('[39]','betaine',7.9,400),('[47]','sulfuric acid',13.5,410),('[24]','nitric acid',23,420),('[49]','2,4-diaminobenzenesulfonic acid',30.5,530),('[19]','3-aminophenylboronic acid',None,514)]: secondary('F20',ref,'lignin',agent,'Table1 does not provide synthesis temperature/time',q,em=str(em))
# F18 gives molecular-weight features useful to PET/lignin co-precursor selection, but primary paper absent.
for lab,mw,pdi,qy in [('AL',3864,6.9,1.31),('F1',7154,2.8,2.26),('F3',5042,2.1,3.86),('F5',2096,2.1,1.04)]:
    secondary('F18','[90]','alkali lignin fraction '+lab,None,f'fractionation;hydrothermal180C8h;precursorMw={mw}g/mol;PDI={pdi}',qy,size='2.2-2.6 group range',em='500',note='原始文献B02未在本地提供；数据为综述转述。')
for ref,agent,temp,h,q,size,em in [('[94]','o-ABSA+NaOH',200,12,21,'2.2','484'),('[96]','3-aminophenylboronic acid',200,12,None,'3.82','346/428/514'),('[97]','o-ABSA',200,16,23.68,'4.8','476'),('[98]','4-aminobenzoic acid',200,12,10.8,'2.88','344'),('[98]','p-ABSA',200,12,7.3,'4.01','360'),('[98]','benzenesulfonic acid',200,12,23.6,'4.56','470'),('[98]','2,4-diaminobenzenesulfonic acid',200,12,30.5,'5.05','530')]: secondary('F18',ref,'alkali lignin',agent,f'acidolysis then hydrothermal{temp}C{h}h',q,size=size,em=em,note='原文未核查；[96]QY原表5-7%。' if ref=='[96]' else None)
for h,q in [(8,8.1),(16,11.6),(24,13)]:
    secondary('F18','[129]','Kraft lignin','H2SO4/HNO3',f'pyrolytic carbon then acid oxidation90C{h}h',q,size='2.4',em='560',ratio='0.1g/20mL acid',note='p15 Table5；原始B05全文缺失，保留二次数据；不可将酸氧化时间当水热时间。'); R[-1]['source_locator']='p15 Table5'

# Trace every supplied file, including duplicates and absent full texts in the previous bibliography.
id_to_study={v[0]:k for k,v in studies.items()}; sources=[]
reviewmeta={'F16':('C02',2025,'10.1002/EXP.70039','Applications of Lignin-Dervied Carbon Quantum Dots: Current Status and Challenges'),'F17':('C04',2024,'10.1016/j.ijbiomac.2024.132897','State-of-the-art of lignin-derived carbon nanodots: Preparation, properties, and applications'),'F18':('C01',2026,'10.1016/j.mtsust.2026.101406','A roadmap of lignin-derived carbon dots: A systematic review of synthesis parameters to obtain desired optical properties'),'F19':('C03',2025,'10.1002/aesr.202500187','Lignin as a Renewable Precursor for Carbon Quantum Dots: Synthesis, Doping Strategies, and Applications'),'F20':('C05',2022,'10.1213/j.issn.2096-2355.2022.03.006','Review of Carbon Dots from Lignin: Preparing, Tuning, and Applying')}
for x in manifest:
    if int(x['file_id'][1:]) >= 23: continue
    fid=x['file_id']; study=id_to_study.get(fid); kind='original_research' if study else 'supporting_information' if fid in ['F08','F09'] else 'review' if fid in reviewmeta else 'existing_bibliography' if fid=='F02' else 'project_context'
    dup='F10' if fid=='F11' else 'F12' if fid=='F13' else None
    if dup: kind='duplicate'; study=id_to_study[dup]
    if fid=='F08': study='A02'
    if fid=='F09': study='A01'
    meta=studies.get(study)
    title=meta[4] if meta else reviewmeta[fid][3] if fid in reviewmeta else x['file']
    doi=meta[3] if meta else reviewmeta[fid][2] if fid in reviewmeta else None
    status='全文参数与数值提取' if study and not dup else '重复文件不重复计数' if dup else '二次表格选取，原始文献核验前不并入训练' if fid in ['F18','F19','F20'] else '背景/路线与引文索引；未构造独立实验行' if fid in ['F16','F17'] else '项目背景或已有摘要库，未作为新测量'
    sources.append(dict(source_file_id=fid,study_id=study or (reviewmeta[fid][0] if fid in reviewmeta else None),file_name=x['file'],title=title,year=meta[1] if meta else reviewmeta[fid][1] if fid in reviewmeta else None,doi=doi,source_kind=kind,pages=x.get('pages'),duplicate_of=dup,sha256=x['sha256'],extraction_status=status))
for source in sources:
    source['file_name']=source['file_name'].replace('/','\\')
missing=[('A09','10.1016/j.ijbiomac.2024.131005','椰壳木质素CD/卡拉胶包装膜'),('B01','10.1016/j.ijbiomac.2025.147132','EDA-Kraft木质素CD的30组CCD/RSM优化'),('B02','10.1039/D3GC04694J','木质素分子量与碳点性质'),('B04','10.1016/j.ccst.2024.100218','HNO3用量与结构光学性质'),('B05','10.1016/j.jiec.2018.06.005','碳化后混酸氧化木质素CD'),('B06','10.1016/j.biombioe.2026.109293','碱木质素碳点合成与Fe3+检测')]
for st,doi,title in missing: sources.append(dict(source_file_id=None,study_id=st,file_name=None,title=title,year=None,doi=doi,source_kind='full_text_absent',pages=None,duplicate_of=None,sha256=None,extraction_status='已有文献目录有记录，本地无对应全文；不从摘要填实验值。'))

# Derived endpoint conversions are explicit and retain a parent measurement ID.
original=list(M)
for row in original:
    if row['endpoint']=='bacterial_survival_pct' and row['value'] is not None and row['regression_eligible']==1:
        other=row.copy(); other['measurement_id']=f'M{len(M)+1:04}'; other['endpoint']='bacterial_killing_pct'; other['value']=round(100-row['value'],8); other['data_status']='derived'; other['value_raw']=f'100 - {row["value"]}'; other['notes']=(other['notes'] or '')+f' 派生自{row["measurement_id"]}；不能同时作为独立训练样本。'; M.append(other)

# An antibacterial learning table: one row per reported assay endpoint, joined only to its parent CD.
additional_routes,additional_queue=append_records(syn,ingredient,proc,form,meas,issue,R)
extend_sources(sources,manifest)
sm={r['sample_id']:r for r in S}; fm={r['formulation_id']:r for r in F}; train=[]
props=collections.defaultdict(dict)
for row in M:
    if row['entity_id'] in sm and row['endpoint'] in ['diameter_TEM_nm','PLQY_pct','singlet_oxygen_QY_pct','XPS_N_pct','XPS_O_pct','PL_lifetime_ns'] and row['regression_eligible']==1 and row['value'] is not None: props[row['entity_id']][row['endpoint']]=row['value']
antibacterial={'bacterial_survival_pct','bacterial_inhibition_pct','bacterial_killing_pct','bacterial_inactivation_pct','bacterial_colony_reduction_pct','zone_of_inhibition_mm','contact_growth_inhibition','zone_observation','bacterial_colony_observation','microbial_penetration_growth'}
antibacterial.update({'MIC_ug_mL','MIC50_ug_mL','MBC_ug_mL','bacterial_log10_reduction'})
for row in M:
    if row['endpoint'] not in antibacterial: continue
    f=fm.get(row['entity_id']); sid=f['parent_sample_id'] if f else row['entity_id']; s=sm.get(sid,{})
    tr={k:row[k] for k in ['measurement_id','entity_id','study_id','endpoint','value','relation','value_low','value_high','uncertainty','unit','data_status','regression_eligible','organism','strain','gram','dose_ug_mL','dose_basis','disk_mass_ug','disk_diameter_mm','material_mass_g','assay_volume_mL','initial_CFU_mL','initial_OD600','contact_min','incubation_h','temperature_C','medium','pH','light','wavelength_nm','wavelength_relation','irradiance_mW_cm2','lamp_power_W','H2O2_mM','cofactor','control','n','material_context','source_file_id','source_locator','notes']}
    tr['sample_id']=sid; tr['pet_present']=0; tr['precursor']=s.get('precursor'); tr['synthesis_temperature_C']=s.get('temperature_C'); tr['synthesis_time_h']=s.get('time_h'); tr['precursor_mass_g']=s.get('precursor_mass_g'); tr['water_mL']=s.get('water_mL'); tr['additive']=s.get('additive'); tr['additive_precursor_mass_ratio']=s.get('additive_precursor_mass_ratio'); tr['additive_loading_pct']=s.get('additive_loading_pct'); tr['loading_basis']=s.get('loading_basis'); tr['cd_loading_pct']=f.get('cd_loading_pct') if f else None; tr['cd_bath_ug_mL']=f.get('cd_bath_ug_mL') if f else None; tr['coactive']=f.get('coactive') if f else None
    for ep in ['diameter_TEM_nm','PLQY_pct','singlet_oxygen_QY_pct','XPS_N_pct','XPS_O_pct','PL_lifetime_ns']: tr['measured_'+ep]=props.get(sid,{}).get(ep)
    tr['split_group']=row['study_id']; tr['PET_recipe_label_available']=0
    tr['intrinsic_CD_evidence']='free_CD' if row['material_context']=='free_CD' else 'requires_H2O2' if row['material_context']=='free_CD_with_H2O2' else 'composite_or_control'
    tr['PET_transfer_use']='hypothesis_only_no_PET_validation'
    tr['default_training_use']='exclude_conflict' if row['data_status']=='conflict' else 'exclude_no_numeric_label' if row['value'] is None else 'qualitative_only' if row['data_status']=='qualitative' else 'exclude_reported_zero_censoring' if row['relation']=='reported_zero' else 'derived_do_not_duplicate' if row['data_status']=='derived' else 'exclude_source_flag' if not row['regression_eligible'] else 'separate_cofactor_assay' if row['material_context']=='free_CD_with_H2O2' else 'separate_composite_assay' if row['material_context']!='free_CD' else 'nonPET_transfer_evidence'
    train.append(tr)

routes=[
dict(route_id='T01',study_id='A01',candidate='木质素 + 乙二胺',evidence_sample=a01[3],reported_method='水热200°C12h；EDA原文6wt%（分母不明）',activity_evidence='游离N,L-CQDs3；30ug/mL；S.aureus99.57%、E.coli93.60%（浓度筛选）',required_condition='氙灯100mW/cm²；15min（FigS5）',intrinsic_evidence='游离碳点光激活抗菌',PET_validation='无PET共同前驱体实测',transfer_limit='可作为PET+木质素/EDA候选假设；不能直接把6wt%当作PET基准用量。'),
dict(route_id='T02',study_id='A02',candidate='木质素 + 草酸',evidence_sample=a02[1],reported_method='酸:AL等质量；水热180°C12h；AL绝对质量缺失',activity_evidence='LCDs-OA40ug/mL；E.coli存活2.6±0.1%、S.aureus1.3±0.2%',required_condition='H2O2；pH4.5；37°C4h',intrinsic_evidence='碳点催化辅助抗菌',PET_validation='无PET共同前驱体实测',transfer_limit='需外部过氧化氢，不能直接作为无辅助自抗菌标签。'),
dict(route_id='T03',study_id='A03',candidate='植物来源木质素纳米粒',evidence_sample=a03,reported_method='LNP:水1:30g:mL；水热180°C12h；不加催化剂',activity_evidence='50ug/纸片；24h S.aureus21.77±0.57mm、K.pneumoniae20.27±1.30mm',required_condition='37°C培养24h；试验未指定光激活',intrinsic_evidence='游离LQD纸片扩散抗菌',PET_validation='无PET共同前驱体实测',transfer_limit='抑菌圈受扩散影响；不是PET+木质素的MIC/杀菌率证据。'),
dict(route_id='T04',study_id='A04',candidate='椰壳碳 + 邻苯二胺',evidence_sample=a04,reported_method='20mg椰壳碳+50mg o-PDA；180°C12h',activity_evidence='游离CD减菌约15-20%；浓度单位冲突',required_condition='接触4h；剂量mg/mL与ug/mL冲突',intrinsic_evidence='有游离CD弱抗菌描述但数值有歧义',PET_validation='无PET共同前驱体实测',transfer_limit='先核查原文/作者；Hg复合结果排除PET候选。'),
dict(route_id='T05',study_id='A05',candidate='木质素 + H2O2',evidence_sample=a05,reported_method='100mg/30mL水+2mL30%H2O2；180°C10min',activity_evidence='CD500修饰TFC膜，UV下E.coli99.92±0.03%',required_condition='PDA/TFC基底；UV365nm3h',intrinsic_evidence='仅复合膜证据',PET_validation='无PET共同前驱体实测',transfer_limit='不能把膜抗菌率标为游离CD抗菌率。'),
dict(route_id='T06',study_id='A06',candidate='Kraft木质素',evidence_sample=a06,reported_method='1.05g/35mL水；180°C5.5h',activity_evidence='GMA/CD水凝胶前驱液接触抑菌，未见抑菌圈',required_condition='GMA/明胶基质',intrinsic_evidence='仅水凝胶前驱液证据',PET_validation='无PET共同前驱体实测',transfer_limit='无游离CD定量抗菌标签。'),
dict(route_id='T07',study_id='A07',candidate='Kraft木质素（姜黄素另列）',evidence_sample=a07,reported_method='2.5wt%木质素水溶液；180°C5.5h',activity_evidence='PLA/CD与PLA/CD/Cur纤维接触抑菌；未见抑菌圈',required_condition='PLA纤维；部分配方含10wt%姜黄素',intrinsic_evidence='仅复合纤维证据',PET_validation='无PET共同前驱体实测',transfer_limit='姜黄素独立活性/PLA屏障不可归因于CD。'),
dict(route_id='T08',study_id='A08',candidate='酶解木质素 + 柠檬酸',evidence_sample=a08,reported_method='1g木质素+0.8g柠檬酸/20mL水；220°C12h',activity_evidence='PVA20%LCQD膜；45min可见光S.aureus杀菌88.44%；E.coli100%',required_condition='PVA复合膜；氙灯300W λ>420nm',intrinsic_evidence='仅复合膜证据',PET_validation='无PET共同前驱体实测',transfer_limit='不能用复合膜结果证明PET碳点本体抗菌。'),
dict(route_id='T09',study_id='B03',candidate='木质素 + 邻氨基苯磺酸',evidence_sample=b03[0],reported_method='AL0.8g+o-ABSA0.6g/30mL水70°C1h；分级后200°C12h',activity_evidence='QY19.5%、产率16.5%；本研究无抗菌试验',required_condition='抗菌终点未测',intrinsic_evidence='仅合成/构效证据',PET_validation='无PET共同前驱体实测',transfer_limit='荧光增强不等于抗菌增强；未测抗菌不得标0或1。')]

pet_fields=['experiment_id','batch_id','pet_source','pet_mass_g','pet_pretreatment','co_precursor','co_precursor_mass_g','dopant','dopant_mass_g','dopant_volume_mL','solvent','solvent_volume_mL','initial_pH','method','temperature_C','time_h','purification','CD_yield_pct','diameter_TEM_nm','zeta_mV','XPS_N_pct','PLQY_pct','organism','strain','initial_CFU_mL','CD_dose_ug_mL','light','wavelength_nm','irradiance_mW_cm2','contact_min','assay_pH','assay_temperature_C','H2O2_mM','assay_method','endpoint','value','unit','control','replicate_n','uncertainty','notes']

figure_queue=[
dict(study_id='A01',entity_id='A01-S01 to A01-S05',source_file_id='F09',source_locator='FigS2',data_to_extract='五组Zeta电位',available_conditions='样品名称明确；仅图示',handling='尚未数字化柱高；无明确文字值不填zeta_mV。'),
dict(study_id='A01',entity_id='A01-S01 to A01-S05',source_file_id='F05',source_locator='p8 Fig5A-B',data_to_extract='各CD的逐时间存活率',available_conditions='S.aureus暗/5/10/15min；E.coli暗/5/10/15/20min',handling='除正文明确零存活外，各柱高度未数字化；不估读填百分数。'),
dict(study_id='A01',entity_id='A01-S01 to A01-S05',source_file_id='F09',source_locator='FigS5',data_to_extract='逐剂量、逐样品抗菌数据',available_conditions='光照15min与无光对照；浓度0-30ug/mL',handling='只提取正文明确N,L-CQDs3的30ug/mL端点；其余图柱待数字化。'),
dict(study_id='A01',entity_id=fa01,source_file_id='F09',source_locator='FigS8-S9',data_to_extract='水凝胶逐CD加入量/储存期抑菌径向距离',available_conditions='0-50mg范围，明确提及5/30/40/50mg；储存5/10/15days',handling='最佳30mg保留；未逐点读取距离，不能当作ZOI直径。'),
dict(study_id='A02',entity_id='A02-S01 to A02-S04',source_file_id='F08',source_locator='FigS10-S12',data_to_extract='TA/CA与OA比较的POD/CAT曲线',available_conditions='有机酸类型确定；POD/CAT不同底物与反应时间',handling='只有明确标数的表格常数提入性能测量，其余曲线不估值。'),
dict(study_id='A02',entity_id=a02[1],source_file_id='F04/F08',source_locator='Fig5; FigS17',data_to_extract='LCDs-OA逐剂量/时间抗菌存活率',available_conditions='0/20/30/40/50ug/mL；4h；存在H2O2',handling='保留正文40ug/mL数值与50ug/mL无菌落观察；其他图点待提取。'),
dict(study_id='A02',entity_id=fcao,source_file_id='F08',source_locator='FigS18',data_to_extract='LCDs-OA@CaO2逐剂量抗菌',available_conditions='0/50/75/100ug/mL；无外加H2O2',handling='保留正文75ug/mL端点；其余图点待数字化。'),
dict(study_id='A04',entity_id=a04,source_file_id='F07',source_locator='p10 Fig5',data_to_extract='CD/Hg复合的剂量-菌落结果',available_conditions='方法和结果剂量单位冲突',handling='先核查单位，不能通过读图消除原文浓度冲突。'),
dict(study_id='A05',entity_id='A05-F01 to A05-F06',source_file_id='F15',source_locator='Fig5-Fig8',data_to_extract='CD300等缺失文字数值、预UV老化与废水条件曲线',available_conditions='暗/3500K日光/365nmUV；3h；预UV3/6/9/15/24h',handling='正文明确数值已提取，其余图点与B.subtilis零检出待核查，不自动填100%。'),
dict(study_id='A08',entity_id='A08-F01 to A08-F04',source_file_id='F14',source_locator='p8 Fig6',data_to_extract='PVA系列完整时间-存活率曲线',available_conditions='正文明确15/45min已记录；方法取样间隔与图/结论冲突',handling='其余图点未估读；逐时间定义需核对。')]
guide=[
('目标','固定PET为主前驱体，预测搭配原料/掺杂剂与制备条件，使所得游离碳点具有抗菌性能。当前文件只提供非PET文献证据。'),
('当前覆盖','9篇去重原始研究（8篇有抗菌相关试验+1篇合成机理）；2份SI；5篇综述；2份PDF为重复版本；原目录6篇没有本地全文。'),
('本体抗菌数值覆盖','当前明确、非冲突、非派生的游离CD数值抗菌终点只有6条，来自2个CD样品（A01-S04、A03-S01）；另有依赖H2O2的纳米酶、复合体系与定性结果。6条不是6种独立配方，且端点/试验协议不同。'),
('数据含义','样品行是文献样品/配方，不代表独立合成批次。重复菌种、光照、剂量和端点行不能当作独立配方样本数。'),
('PET限制','文献样本pet_present=0；不存在PET配方-抗菌实测标签。不能仅用此库训练并声称已验证PET最优配方。PET实验录入为零行空模板，无虚构实验。'),
('优先证据','T01游离CD光动力；T03游离LQD抑菌圈；T02依赖H2O2；T04浓度冲突。复合膜/水凝胶与Hg复合不作为CD本体固有活性标签。'),
('标签分开','MIC、MBC、抑菌圈mm、存活率%、杀菌率%、接触抑菌二元观察分别建模。本地全文直接提取未得到明确数值MIC/MBC，不用抑菌圈/零菌落替代。'),
('光照','未写光照=未知，不擅自记dark；实验设置dark才填dark。lamp_power_W是灯额定功率，不能换算irradiance_mW_cm2。'),
('浓度','CD修饰浴浓度、游离CD测试剂量、复合膜总质量、纸片CD质量分列。复合物剂量不能等同碳点净剂量。'),
('百分数','百分数字段使用0-100数值；例如99.57表示99.57%，不使用0.9957。质量比g/g用无量纲小数。'),
('缺失','空单元格/CSV空字段/JSON null表示未明确报告、未能可靠提取或不适用；见missing_fields与notes。缺失不能填0。'),
('数值状态','reported原文明确；reported_figure_label图内清楚数值标签且已目视核对；unit_converted单位换算；derived按明确式换算；reported_range原文范围；group_range多个样品共同范围；conflict原文冲突；qualitative定性。'),
('零与范围','reported_zero原文检出限内零存活；保留0但默认排除普通回归。范围填low/high不取中点；无抑菌圈不填0mm。'),
('派生数据','杀菌率=100-存活率，派生行注明原measurement_id。选择原行或派生行之一；不把两者当两个独立观测。'),
('训练筛选','regression_eligible只表示数值提取可作数值候选，不代表协议已统一或适合PET。本体模型需再选material_context=free_CD，并审核光照与剂量。'),
('数据切分','split_group=study_id；先按论文分组，进一步按共同CD合成样品分组；同配方不同光照/菌种/时间不可跨训练和测试集。'),
('避免信息泄漏','从配方预测活性时，measured_粒径、N含量、ROS/QY属于制备后表征，先不作为纯配方模型输入；可用于独立的两阶段模型。'),
('PET实验对照','后续至少记录PET单独、PET+木质素/掺杂剂、非碳化原料/游离掺杂剂、空白溶剂与相同光照对照；透析/纯化后测游离CD，区分残余试剂贡献。'),
('逆向筛选方法','先用匹配协议的PET实测抗菌标签建立正向预测，再在允许的共前驱体与工艺空间排序；本库可支持候选假设和特征设计，不能直接给出经验证最优参数。'),
('样本不平衡','文献偏向报告有效材料；未做抗菌测试的CQDs不标负例；纯聚合物/无CD对照不是失败的CD合成样品。'),
('综述','二次数据仅作追文献与候选原料索引；未与直接全文数据合并，也未完成跨综述所有原始DOI去重。T01-T09基于本地全文。'),
('来源定位','PDF页码一律从文件第一页起算，可能与期刊印刷页不同；SI用Table/Figure或XML段落P编号定位。'),
('范围说明','重点提取配方、前处理、合成、纯化、复合制备、粒径/光学/XPS/纳米酶和抗菌数值；动物创面图、完整谱图、所有图线点及复合材料全部力学数据未逐点数字化。'),
('复核队列','待核查表记录单位冲突、缺失配方、图表矛盾；图中只有曲线/柱高而无数值标签的点不估读填数。'),
('更新日期','2026-10-16；仅以用户本地提供文件为依据，没有联网补全文或混入摘要推测值。')]

routes.extend(additional_routes)
figure_queue.extend(additional_queue)
free_exact=[r for r in train if r['material_context']=='free_CD' and r['regression_eligible']==1 and r['data_status']!='derived']
updates={
    '当前覆盖':'在原22份文件上追加抗菌目录20份PDF及单独综述1份。合计22篇去重原始研究（19篇有抗菌相关试验、3篇合成/机制背景）、3份SI、12篇综述、原2份重复PDF及4份项目背景。原目录6篇缺文仍保留。',
    '本体抗菌数值覆盖':f'当前明确、非冲突、非派生且regression_eligible=1的游离CD抗菌终点{len(free_exact)}条，来自{len({r["sample_id"] for r in free_exact})}个CD样品。MIC/MIC50/MBC/抑菌圈/失活率不可混成单一标签，条数不等于独立配方数。',
    '标签分开':'新增MIC、MIC50、MBC及log10降低量端点，分别储存；MIC50是50%抑制，不能当无可见生长MIC。剂量计量对象见dose_basis；含PpIX当量的结果不当CD净质量。',
    '综述':'原始全文与综述二次机制/区间/AI表格继续分开。新增C12为用户指定精读综述，含异质MIC区间、机制与AI/ML索引；不将综述类别范围展开为实验行。T01-T20为原始研究路线索引，不含PET验证。',
    '来源定位':'PDF页码从文件第一页起算；旧F01-F22文件名相对木质素文献内层目录；新F23-F43文件名相对项目根目录。SI/综述与主文共享研究ID以防重复计数。',
    '范围说明':'重点覆盖配方、制备/纯化、原文明确抗菌数值及粒径/电荷/XPS/光学性质；新增微波/熔融/电化学过程。未逐点数字化全图；动物伤口/食品保存/完整组学和力学数据未当作CD本体抗菌标签。D12作物抗氧化、D13苯酚降解、C11 MXene只作背景。',
}
guide=[(a,updates.get(a,b)) for a,b in guide]
guide.append(('本次增补与模型版本','2026-10-16补充“抗菌文献”及指定机制综述；保留旧样品/M/C/P/R编号和原始记录。首版CUDA模型继续对应其已冻结的16行A08数据，本次不自动重训或覆盖模型。'))
tables={'路线筛选':routes,'抗菌训练长表':train,'碳点合成':S,'配方组分':C,'工艺步骤':P,'复合体系':F,'性能测量':M,'综述二次数据':R,'来源与缺文':sources,'待核查':Q,'图表补录索引':figure_queue,'PET实验录入':[],'建库说明':[{'topic':a,'description':b} for a,b in guide]}
headers={k:list(v[0]) if v else pet_fields for k,v in tables.items()}

# Compact bilingual schema. Units live in names and dedicated unit fields; no implicit zero imputation.
labels={
'route_id':('路线ID','标识'), 'study_id':('文献ID，与已有库对应','分组键'), 'sample_id':('碳点样品ID','主键/关联键'), 'entity_id':('被测/被加工实体ID，可为样品或复合体系','关联键'), 'sample_label':('原文样品名','标识'), 'formulation_id':('复合配方ID','主键'), 'parent_sample_id':('所用碳点样品ID；对照为空','关联键'), 'measurement_id':('性能记录ID','主键'), 'component_id':('组分记录ID','主键'), 'process_id':('工艺步骤ID','主键'), 'secondary_id':('综述数据ID','主键'), 'source_file_id':('F编号，见来源与缺文','出处'), 'source_locator':('PDF文件页/章节/图表；或SI段落','出处'), 'notes':('关键定义、缺失和歧义说明','备注'), 'source_kind':('文件类型/全文缺失/重复','出处'), 'source_level':('来源层级','出处'), 'pet_present':('PET是否实际参与文献制备，0=无，1=有','候选特征'), 'precursor':('碳源/前驱体原文身份','输入'), 'precursor_supplier':('前驱体供应商','输入'), 'precursor_fraction':('木质素分级组分','输入'), 'method':('测定方法，合成表中为制备方法','条件'), 'temperature_C':('该表所述步骤/测试温度','°C'), 'time_h':('碳点水热保温时间','h'), 'water_mL':('明确的水加入体积','mL'), 'precursor_mass_g':('实际碳点制备前驱体质量；不含共同酸解批次','g'), 'precursor_conc_mg_mL':('按明确水体积计算的前驱体质量浓度','mg/mL'), 'precursor_conc_raw':('原文浓度/质量体积关系','原文'), 'additive':('合成添加剂/掺杂剂','输入'), 'additive_mass_g':('合成添加剂绝对质量','g'), 'additive_volume_mL':('合成添加剂/原液体积','mL'), 'additive_loading_pct':('原文添加百分数，分母另列','0-100百分数'), 'loading_basis':('添加百分数的分母定义','条件'), 'additive_precursor_mass_ratio':('添加剂质量/前驱体质量，来源明确才换算','g/g'), 'initial_pH':('碳点反应起始pH','pH'), 'reactor_mL':('反应釜标称容量，非溶液体积','mL'), 'sonication_min':('合成前超声时长','min'), 'centrifuge_rpm':('离心转速，不混同g相对离心力','rpm'), 'centrifuge_min':('离心时长','min'), 'filter_um':('过滤孔径','um'), 'dialysis_MWCO_Da':('透析截留分子量','Da'), 'dialysis_h':('透析总时长','h'), 'freeze_dry_C':('冻干温度，不混同预冻温度','°C'), 'freeze_dry_h':('冻干时长','h'), 'storage_C':('储存温度','°C'), 'missing_fields':('原文/当前资料不能明确获得的重要字段','缺失说明'), 'stage':('步骤所属阶段：提取/合成/纯化/复合等','条件'), 'step_order':('同实体记录顺序；不表示所有操作均被拆为单步','序号'), 'operation':('工艺操作及必要原文条件','条件'), 'duration_h':('该步时长；周期工艺见备注','h'), 'pH':('该步骤或测试介质pH','pH'), 'volume_mL':('该步明确溶液体积','mL'), 'speed_rpm':('搅拌/离心转速，具体性质见operation','rpm'), 'pressure_bar':('原文工艺压力，表压/绝压未另作推断','bar'), 'chemical_name':('组分化学名/试剂形态','输入'), 'role':('组分角色','输入'), 'amount':('组分加入量或比值，结合unit/denominator','数值'), 'unit':('数值单位；%按0-100储存','单位'), 'amount_raw':('原文量值及基准','原文'), 'denominator':('浓度/质量比的分母或比例基准','条件'), 'formulation_label':('原文复合配方名','标识'), 'matrix':('基体；none表示未引入聚合物基体','条件'), 'cd_loading_pct':('复合体系CD添加百分数，结合基准列','0-100百分数'), 'cd_loading_basis':('CD质量百分数分母','条件'), 'cd_mass_mg':('配方批次CD加入量，不是测试剂量','mg'), 'cd_bath_ug_mL':('膜修饰浴CD浓度，不是实测膜负载或给药浓度','ug/mL'), 'coactive':('其他潜在活性组分','混杂因素'), 'coactive_loading_pct':('其他活性组分添加百分数','0-100百分数'), 'matrix_mass_g':('主基体投料质量，其他基体见组分表','g'), 'processing':('复合加工方法','条件'), 'endpoint':('测量端点，不同端点不直接混合','标签名'), 'value':('原文明确单值；不以中点替代范围','标签/性质数值'), 'relation':('=、approximately、range、reported_zero等','数值限定'), 'value_low':('范围下界，不是均值','同unit'), 'value_high':('范围上界，不是均值','同unit'), 'uncertainty':('原文±后的数值','同unit'), 'uncertainty_type':('SD明确标准差；not_specified原文未定义','限定'), 'value_raw':('原文量值或转换式','溯源'), 'organism':('菌种/细胞系；不能混为同一终点','测试条件'), 'strain':('菌株编号或原文MDR；不推定来源','测试条件'), 'gram':('革兰阴/阳性，按所列物种','测试条件'), 'dose_ug_mL':('测试液中游离CD或明确复合物剂量；看dose_basis','ug/mL'), 'dose_basis':('剂量对应对象','条件'), 'disk_mass_ug':('每个扩散纸片上CD质量','ug/disk'), 'disk_diameter_mm':('纸片直径','mm'), 'material_mass_g':('抗菌试验中的复合膜质量','g'), 'assay_volume_mL':('测试液体积','mL'), 'initial_CFU_mL':('初始菌浓度','CFU/mL'), 'initial_OD600':('初始菌液600nm光密度，不换算CFU','OD'), 'contact_min':('抗菌处理/照射接触时间','min'), 'incubation_h':('平板后续培养或细胞暴露时间，见method','h'), 'medium':('测试培养基/盐水/缓冲液','测试条件'), 'light':('明确光照状态；缺失不等于dark','测试条件'), 'wavelength_nm':('光源波长/截止波长；PL行看method','nm'), 'wavelength_relation':('>等波长截止限定','限定'), 'irradiance_mW_cm2':('样品处光功率密度','mW/cm²'), 'lamp_power_W':('光源额定功率，不推算功率密度','W'), 'H2O2_mM':('抗菌外加H2O2浓度；0仅用于明确无外加','mM'), 'cofactor':('过氧化物/金属等辅助条件','混杂因素'), 'control':('该端点的参照/对照','定义'), 'n':('原文重复数或颗粒计数，见method/notes','计数'), 'material_context':('free_CD/含H2O2/复合膜/水凝胶等材料层级','训练筛选'), 'data_status':('reported/converted/derived/range/conflict/qualitative','质量标记'), 'regression_eligible':('1仅表示可作为明确数值候选；不等于可直接训练PET','训练筛选'), 'evidence_text':('原文结果短语，优先保留定性信息','证据'), 'split_group':('分组切分使用study_id','防泄漏'), 'PET_recipe_label_available':('0表示当前无PET共同制备抗菌实测','覆盖限制'), 'intrinsic_CD_evidence':('游离CD/需H2O2/复合或对照','证据分类'), 'PET_transfer_use':('当前仅假设来源，无PET验证','覆盖限制'), 'default_training_use':('默认模型用途/排除原因','训练筛选'), 'synthesis_temperature_C':('关联原始CD制备温度','°C'), 'synthesis_time_h':('关联原始CD制备时间','h'), 'include_primary_training':('综述数据固定0，追原文前不并入直接数据','训练筛选'), 'original_reference':('综述中的参考文献编号，需原文索引解析','出处'), 'conditions_raw':('综述转述条件，不能当原始实测','条件'), 'diameter_raw_nm':('综述粒径文本，保留范围','nm'), 'emission_raw_nm':('综述发射波长文本','nm'), 'ratio_raw':('综述原始配比文本，多组分保持次序','原文'), 'yield_raw_pct':('综述产率文本，保留范围','%'), 'PLQY_pct':('荧光量子产率，与单线态氧QY不同','%'), 'file_name':('相对于用户文献根目录的文件名','出处'), 'title':('文献题名/项目文件名','出处'), 'year':('论文发表年','年'), 'doi':('DOI；未联网补齐','出处'), 'pages':('PDF文件总页数','页'), 'duplicate_of':('重复文件对应保留F编号','去重'), 'sha256':('本地文件SHA256用于精确复核','溯源'), 'extraction_status':('实际提取范围/未提供全文状态','覆盖限制'), 'issue_id':('疑点ID','标识'), 'field':('受影响字段','核查'), 'issue':('原文具体冲突/疑点','核查'), 'handling':('本库处理方式','核查'), 'candidate':('与PET搭配的候选材料假设来源','筛选'), 'evidence_sample':('支撑路线的文献CD样品','关联键'), 'reported_method':('文献实际方法；未经PET验证','条件'), 'activity_evidence':('文献实际抗菌证据摘要','标签依据'), 'required_condition':('活性测试所需辅助条件','条件'), 'intrinsic_evidence':('是否有游离CD活性证据','筛选'), 'PET_validation':('是否含PET共同前驱体实测','覆盖限制'), 'transfer_limit':('迁移到PET体系的主要限制','建模约束'), 'topic':('使用说明主题','说明'), 'description':('使用说明','说明')}
for ep,unit,zh in [('diameter_TEM_nm','nm','TEM碳点平均粒径'),('PLQY_pct','%','荧光量子产率'),('singlet_oxygen_QY_pct','%','单线态氧量子产率'),('XPS_N_pct','%','XPS氮百分比'),('XPS_O_pct','%','XPS氧百分比'),('PL_lifetime_ns','ns','荧光平均寿命')]: labels['measured_'+ep]=(zh+'，制备后实测特征，纯配方模型有泄漏风险',unit)
labels.update({
'experiment_id':('后续PET实测实验唯一编号','主键'), 'batch_id':('独立合成批次编号；技术重复共用批次','分组键'),
'pet_source':('PET来源/牌号/回收来源及批次','输入'), 'pet_mass_g':('该批PET实际加入质量','g'), 'pet_pretreatment':('PET清洗、粉碎、解聚等实际前处理','输入'),
'co_precursor':('PET以外共同碳前驱体化学名称/来源','输入'), 'co_precursor_mass_g':('共前驱体实际投料质量','g'),
'dopant':('掺杂/钝化试剂具体化学名与浓度','输入'), 'dopant_mass_g':('掺杂剂实际质量；溶液投料须注明溶质基准','g'), 'dopant_volume_mL':('掺杂剂或其原液实际加入体积','mL'),
'solvent':('溶剂种类；混合溶剂比例也记录','输入'), 'solvent_volume_mL':('实际溶剂总体积','mL'), 'purification':('离心/过滤/透析/色谱等实际纯化方法与参数','输入'),
'CD_yield_pct':('CD实测质量产率，必须在notes说明分母PET或总碳源','%'), 'diameter_TEM_nm':('纯化后CD的TEM平均粒径','nm'), 'zeta_mV':('纯化后CD的Zeta电位，notes注明介质/pH','mV'), 'XPS_N_pct':('CD实测XPS氮含量；注明原子分数基准','%'),
'CD_dose_ug_mL':('抗菌测试液中纯化游离CD的实际剂量','ug/mL'), 'assay_pH':('抗菌测试体系pH，区别于合成初始pH','pH'), 'assay_temperature_C':('抗菌接触处理温度，区别于合成温度','°C'),
'assay_method':('抗菌具体方法与培养/读数协议','条件'), 'replicate_n':('该端点实际独立或技术重复数，notes说明类型','计数'),
'data_to_extract':('图中尚未数字化的量值类型','补录索引'), 'available_conditions':('当前已明确的图中测试条件与取值范围','补录索引')})
for k in pet_fields:
    labels.setdefault(k,('PET后续实测录入字段；按列名单位记录，不填推测值','输入/标签/条件'))
dictionary=[]
labels['time_h']=('碳点主合成步骤时长；微波/电化学为通电时间，分阶段/冷却间隔见工艺和备注','h')
for tab,hs in headers.items():
    for key in hs:
        zh,role=labels.get(key,(key,'见列名'))
        dictionary.append(dict(table=tab,field=key,definition_zh=zh,unit_or_role=role,missing_policy='空值不等于0；不得猜测填补'))
endpoint_defs={
'diameter_TEM_nm':'碳点TEM平均粒径；范围与点值分开','height_AFM_nm':'AFM高度，不能替代TEM直径','PLQY_pct':'荧光量子产率','singlet_oxygen_QY_pct':'单线态氧量子产率，不能替代PLQY','mass_yield_pct':'干燥CD质量/该论文指定原料质量×100','PL_lifetime_ns':'文献平均荧光寿命','Raman_IG_ID':'Raman IG/ID；不是ID/IG','Raman_carbonyl_area_pct':'Raman碳酰基拟合峰面积百分比','lattice_spacing_nm':'HRTEM晶格间距','emission_peak_nm':'发射峰波长','excitation_peak_nm':'最强PL激发波长','absorption_peak_nm':'吸收峰波长','precursor_Mw_g_mol':'明确指定木质素前驱体重均分子量','precursor_Mn_g_mol':'明确指定木质素前驱体数均分子量','precursor_PDI':'木质素Mw/Mn；不是DLS粒径分散系数','bacterial_survival_pct':'相对指定对照的细菌存活率','bacterial_killing_pct':'杀菌率；若由存活率转换有derived标记','bacterial_inhibition_pct':'原文称抑菌率，保留该名称','bacterial_inactivation_pct':'附着细菌失活率，指定对照非常关键','bacterial_colony_reduction_pct':'原文菌落减少范围，A04存在单位冲突','zone_of_inhibition_mm':'抑菌圈总径，未扣纸片直径','contact_growth_inhibition':'0/1为定性接触生长抑制观察，不能当百分数','zone_observation':'无可见抑菌圈的定性观察，无数值标签','bacterial_colony_observation':'未检出菌落的定性观察，不强行换成100%','microbial_penetration_growth':'0为屏障后培养液无生长；不是CD杀菌率','cell_viability_pct':'细胞存活百分比，非细菌标签','cell_viability_reduction_pct':'相对细胞存活下降百分比，非细菌标签','fiber_diameter_SEM_nm':'复合纤维SEM直径，非碳点粒径','solution_viscosity_cP':'纺丝前溶液黏度','suspension_CD_mg_g':'CD悬浮液质量浓度，非合成产率','CD_encapsulation_pct':'CD包封效率','curcumin_encapsulation_pct':'姜黄素包封效率'}
endpoint_defs['zone_of_inhibition_mm']='原文抑菌圈ZOI数值，是否包含纸片直径未明确；保留原值，跨论文前核查定义'
endpoint_defs.update({'MIC_ug_mL':'原文最小抑菌浓度；阈值/协议/计量对象见method与dose_basis，未知条件不填补',
    'MIC50_ug_mL':'50%抑制浓度，区别于无可见生长的MIC', 'MBC_ug_mL':'原文最小杀菌浓度；杀菌阈值按该文定义',
    'bacterial_log10_reduction':'原文log10 CFU/mL降低量；不与菌数绝对log或杀菌百分数混合',
    'zeta_mV':'被测实体的zeta电位；介质及pH会改变数值，不视为与配方无关的常数',
    'Raman_ID_IG':'Raman ID/IG，与IG/ID分别储存', 'drug_loading_content_pct':'药物质量/纳米杂化物质量百分比，非CD产率',
    'surface_carboxyl_mmol_g':'表面羧基含量；非抗菌标签'})
for e in sorted({r['endpoint'] for r in M}):
    definition=endpoint_defs.get(e,'XPS表面元素百分比；不自动推断质量分数/原子分数' if e.startswith('XPS_') else '纳米酶米氏常数/最大速率；底物与单位由端点及unit明确')
    dictionary.append(dict(table='性能测量 endpoint枚举',field=e,definition_zh=definition,unit_or_role=next(r['unit'] for r in M if r['endpoint']==e),missing_policy='无测量不标0/负例'))
tables['字段字典']=dictionary; headers['字段字典']=list(dictionary[0])

def writecsv(name,rows,hs):
    with (CSV/f'{name}.csv').open('w',encoding='utf-8-sig',newline='') as out:
        w=csv.DictWriter(out,fieldnames=hs); w.writeheader(); w.writerows(rows)
for name,rows in tables.items(): writecsv(name,rows,headers[name])
payload={'tables':tables,'headers':headers,'summary':{k:len(v) for k,v in tables.items()}}
(ROOT/'tmp'/'database.json').write_text(json.dumps(payload,ensure_ascii=False,indent=2),encoding='utf-8')
readme='# PET共前驱体筛选用木质素碳点文献数据库\n\n'+'\n\n'.join(f'## {a}\n\n{b}' for a,b in guide)+'\n\n## 数据量\n\n'+'\n'.join(f'- {k}：{len(v)}行' for k,v in tables.items())+'\n\n原始文件不作修改。CSV采用UTF-8 BOM，空字段表示缺失。以字段字典解释单位与列含义。\n'
(OUT/'建库与建模说明.md').write_text(readme+REVIEW_READING,encoding='utf-8')
with zipfile.ZipFile(OUT/'机器学习CSV数据包.zip','w',zipfile.ZIP_DEFLATED) as z:
    for p in sorted(CSV.glob('*.csv')): z.write(p,'csv/'+p.name)
    z.write(OUT/'建库与建模说明.md','建库与建模说明.md')
print(json.dumps(payload['summary'],ensure_ascii=False))

# Data-integrity checks, independent of Excel rendering.
assert len(S)>=20
assert len({r['sample_id'] for r in S})==len(S)
assert len({r['measurement_id'] for r in M})==len(M)
assert all(r['study_id'] in studies for r in M)
assert all(r['pet_present']==0 for r in S)
assert all(r['parent_sample_id'] in sm or r['parent_sample_id'] is None for r in F)
assert all(r['value'] is None or isinstance(r['value'],(int,float)) for r in M)
assert all(0<=r['value']<=100 for r in M if r['unit']=='%' and r['value'] is not None)
print('integrity checks passed')
