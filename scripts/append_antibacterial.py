"""Curated additions from the supplied antibacterial PDFs, 2026-10-16.

Only explicitly reported values are transcribed. All locators use PDF file pages.
Called after the original 250 measurement rows, so their identifiers stay stable.
"""
ADDITIONAL_STUDIES = {
    'D01': ('F24',2025,'Wen','10.1016/j.ijbiomac.2025.141716','Natural fluorescent carbon quantum dots embedded polyvinyl alcohol/chitosan film with photoregulation and high antibacterial efficiency for infected wound healing'),
    'D02': ('F25',2021,'Hao','10.1016/j.msec.2021.111971','Antibacterial activity of positively charged carbon quantum dots without detectable resistance for wound healing with mixed bacteria infection'),
    'D03': ('F26',2023,'Yan','10.1016/j.jmrt.2022.11.090','Green synthesis of carbon quantum dots from plant turmeric holds promise as novel photosensitizer for in vitro photodynamic antimicrobial activity'),
    'D04': ('F29',2025,'Wang','10.1002/adhm.202404770','Self-Capped Carbon Dots with Excellent Anti-Bacteria Effect and an Extremely Low Cytotoxicity Applied for Hand Sanitizer'),
    'D05': ('F31',2025,'Xu','10.1002/advs.202411084','Turning Waste into Treasure: Functionalized Biomass-Derived Carbon Dots for Superselective Visualization and Eradication of Gram-Positive Bacteria'),
    'D06': ('F36',2022,'Qie','10.3389/fbioe.2022.894100','Design, Synthesis, and Application of Carbon Dots With Synergistic Antibacterial Activity'),
    'D07': ('F37',2025,'Zhang','10.1016/j.actbio.2025.05.032','Dextran guanidinylated carbon dots with antibacterial and immunomodulatory activities as eye drops for the topical treatment of MRSA-induced infectious keratitis'),
    'D08': ('F38',2023,'Niu','10.1039/d3tb01376f','Dual enzyme-mimicking carbon dots for enhanced antibacterial activity'),
    'D09': ('F39',2025,'Zhou','10.1016/j.cej.2025.170652','Lysine-derived carbon dots/chitosan synergistic antibacterial composite films for enhanced grape preservation'),
    'D10': ('F40',2021,'Romero','10.3389/fmicb.2021.662149','One-Pot Microwave-Assisted Synthesis of Carbon Dots and in vivo and in vitro Antimicrobial Photodynamic Applications'),
    'D11': ('F42',2022,'Tejwan','10.1016/j.inoche.2022.109317','Synthesis of green carbon dots as bioimaging agent and drug delivery system for enhanced antioxidant and antibacterial efficacy'),
    'D12': ('F30',2025,'Su','10.1002/advs.202506906','Dual-Emission Carbon Dot Nanozymes Mitigate Salt Stress and Enhance Photosynthesis for Crop Germination and Growth'),
    'D13': ('F35',2025,'Xia','10.1016/j.jhazmat.2025.137607','Carbon quantum dots as efficient cocatalysts in Fenton-like processes: Preparation optimization and mechanistic insights'),
}
ADDITIONAL_REVIEWS = {
    'F23':('C06',2024,'10.1016/j.jece.2024.114444','A comprehensive review on nitrogen-doped carbon dots for antibacterial applications'),
    'F27':('C07',2026,'10.1016/j.crfs.2026.101316','The carbon quantum dots: Preparation, antibacterial mechanisms, and application in food packaging'),
    'F32':('C08',2025,'10.1016/j.mtbio.2024.101383','Antibacterial carbon dots'),
    'F33':('C09',2023,'10.1002/adhm.202300324','Antibacterial Carbon Dots: Mechanisms, Design, and Applications'),
    'F34':('C10',2024,'10.3390/nano14151250','Carbon Dots in Photodynamic/Photothermal Antimicrobial Therapy'),
    'F41':('C11',2022,'10.1007/s40820-022-00901-w','Recent Advancements on Photothermal Conversion and Antibacterial Applications over MXenes-Based Materials'),
    'F43':('C12',2026,'10.1007/s00203-026-04962-y','A critical review on antibacterial mechanisms of carbon dots: a comprehensive approach to combating multidrug resistance'),
}

REVIEW_READING = '''
## 指定综述精读：对 PET 配方建模的意义

来源：C12 / F43，Vadakkan 等，2026，DOI 10.1007/s00203-026-04962-y。页码均为所给 PDF 文件页。阅读正文机制、证据局限与 AI/ML 段落，并目视核对 Table 1、Table 2 与相关页面。该综述提出的是跨材料机制框架，没有给出 PET 配方验证。

### 可以采用的机制框架

可以将研究问题组织为“原料与工艺 → 碳点表面/电子结构 → 与菌体及测试环境相互作用 → 抗菌端点”。前驱体官能团、胺基质子化、表面配体和金属配位各有作用，不能只按掺杂元素名称判断活性。金属掺杂不必然让材料带正电（p5–6），zeta 电位必须结合介质、pH、粒径及表面基团解释（p8–10）。D09 赖氨酸碳点的同一样品在不同 pH 下电位不同，是本地原始研究中可直接核对的例子。

ROS 生成、物理膜损伤、DNA/蛋白与能量代谢干扰、群体感应抑制和 EPS 破坏可能重叠，但证据强度不同（p10–18）。荧光探针变亮、加入清除剂后活性下降或转录变化，不能单独证明唯一的因果机制。生物膜量下降也可能来自抑制黏附或基质分散，不能自动当作浮游菌杀菌率。综述提到的 MurD 竞争性抑制在 p13–14 又明确缺少直接动力学/结构证据，本库将它作为机制假设；本地 Qie2022 原文已对应 D06/F36，综述提及不重复计样本。

### 应怎样进入数据库和模型

| 内容 | 当前记录方式 | 后续用途 |
| --- | --- | --- |
| 前驱体身份/投料、溶剂、温度、时间、纯化 | 碳点合成、组分与步骤表，保留原值和缺失 | 配方模型的可用输入 |
| zeta、TEM、XPS、光学和 ROS | 性能长表，绑定样品和测量条件 | 机制分析或两阶段模型；从配方预测时不偷用制备后真值 |
| 菌种/菌株、菌量、剂量计量对象、pH/培养基、光照 | 抗菌长表中的各独立字段 | 与配方共同决定输出，缺失不擅自默认暗/无 H2O2 |
| MIC、MIC50、MBC、失活率、log10 降低量、生物膜 | 各用不同 endpoint；复合物与游离CD分层 | 分任务训练，先统一协议和终点定义 |
| 金属、抗生素、PpIX、芦丁、壳聚糖等 | 共活性组分/复合实体及 dose_basis | 分离外加贡献，不全部归因碳核 |
| Table1 掺杂类别 MIC 区间 | 综述二次数据，include_primary_training=0 | 原始文献追索，不能将区间当精确实验样本 |

Table1 所给金属、非金属、共掺杂等 MIC 范围来自不同菌株、测试方法和激发条件，综述 p8 也明确不宜直接定量比较。因此不以这些区间证明“金属一定优于氮”，也不把它们扩成训练行。

### 这篇综述怎样支持课题必要性

p22–23 的 AI/ML 段落和 Table4 主要列举发射波长、荧光量子产率、光谱及粒径预测。原文同时指出标准数据少，MIC/生物膜等生物学指标纳入不足。这为“把配方、真实抗菌端点和实验环境连起来”的任务提供了文献动机，但不能证明现有模型已经能从 PET 配方预测抗菌，更不能证明使用 LLM 潜空间必然有效。

对本项目而言，可检验的问题是：在统一的菌种、剂量和光照协议下，保留 PET 主前驱体时，搭配原料与制备条件能否预测纯化后游离碳点的活性；这种预测能否迁移到未见过的搭配材料或独立合成批次。传统模型可作为这个问题的基线，以后的 LLM 表征方法需要在相同数据划分和真实实验反馈下比较。此次只更新证据库，没有重训或改写旧模型。

### 阅读时保留的疑点

Fig2 标题将金属掺杂概括为正电，而附近正文明确说金属掺杂不必然正电。Table4 将较高 PLQY 与 ROS/抗菌相关联，但荧光辐射、系间窜越、非辐射及 ROS 反应是不同通道；本库将 PLQY、单线态氧量子产率和抗菌结果分开，拒绝用一个替代另一个。p15 的 MCF7 细胞凋亡/G0-G1 例子属于哺乳动物证据，不能写成细菌抗菌实验。上述疑点已放入“待核查”，不作为确定的因果规则。
'''


def extend_sources(sources, manifest):
    by_file = {v[0]: (k,v) for k,v in ADDITIONAL_STUDIES.items()}
    for x in manifest:
        fid=x['file_id']
        if int(fid[1:]) < 23:
            continue
        if fid in by_file:
            study, meta=by_file[fid]
            year, doi, title=meta[1],meta[3],meta[4]
            kind='original_research'
            status='配方/合成/纯化与明确抗菌数值提取；未逐点数字化图线，缺失SI见核查队列'
            if study in {'D12','D13'}:
                status='合成与机制背景提取；无抗菌试验，不标为抗菌负例'
        elif fid=='F28':
            study='D04'; year=2025; doi='10.1002/adhm.202404770'
            title='Supporting Information: '+ADDITIONAL_STUDIES['D04'][4]
            kind='supporting_information'; status='配方/纯化/抗菌协议提取；与F29为同研究'
        else:
            study,year,doi,title=ADDITIONAL_REVIEWS[fid]
            kind='review'; status='机制与追文献索引；不作独立训练标签'
            if fid=='F43': status='机制精读；Table1/2/4二次索引及批判性解读'
            if fid=='F41': status='MXene光热综述；非碳点原始研究，不纳入CD训练'
        prior=next((s for s in sources if s.get('sha256')==x['sha256']),None)
        sources.append(dict(source_file_id=fid,study_id=study,file_name=x['project_path'],title=title,
                            year=year,doi=doi,source_kind='duplicate' if prior else kind,pages=x['pages'],
                            duplicate_of=prior['source_file_id'] if prior else None,sha256=x['sha256'],
                            extraction_status='重复文件不重复计数' if prior else status))


def append_records(syn, ingredient, proc, form, meas, issue, reviews):
    routes=[]; queue=[]
    def component(entity,st,name,role,amount=None,unit=None,**kw):
        return ingredient(entity,st,name,role,amount,unit,**kw)
    def properties(sid,st,entries,loc):
        for ep,val,unit in entries:
            meas(sid,st,ep,val,unit,loc)
    def graph(st,entity,fid,loc,what,conditions,handling='仅图示且无明确文字/数值标签的点未估读；需另行数字化并记录误差。'):
        queue.append(dict(study_id=st,entity_id=entity,source_file_id=fid,source_locator=loc,
                          data_to_extract=what,available_conditions=conditions,handling=handling))
    def route(st,candidate,sid,method,evidence,condition,intrinsic,limit):
        routes.append(dict(route_id=f'T{10+len(routes):02}',study_id=st,candidate=candidate,evidence_sample=sid,
                           reported_method=method,activity_evidence=evidence,required_condition=condition,
                           intrinsic_evidence=intrinsic,PET_validation='无PET共同前驱体实测',transfer_limit=limit))
    def review(fid,loc,ref,condition,note,precursor=None,additive=None):
        reviews.append(dict(secondary_id=f'R{len(reviews)+1:03}',source_file_id=fid,source_locator=loc,
                            original_reference=ref,precursor=precursor,additive=additive,
                            conditions_raw=condition,PLQY_pct=None,diameter_raw_nm=None,emission_raw_nm=None,
                            ratio_raw=None,yield_raw_pct=None,source_level='secondary_review',
                            include_primary_training=0,notes=note))

    # D01: film material, not an independent free-CD antibacterial assay.
    s=syn('D01','turmeric CDs','turmeric ethanolic extract',180,12,method='solvothermal',filter_um=.22,
          source_locator='p3 §2.2',missing_fields='姜黄萃取投料、乙醇浓度、离心/干燥条件、透析未报告',
          notes='20mL为乙醇提取液，不写入water_mL；与D03制备10h不同，不能视为同一合成样品。')
    component(s,'D01','turmeric ethanolic extract','precursor solution',20,'mL',loc='p3 §2.2')
    proc(s,'D01','CD_synthesis','solvothermal in turmeric ethanolic extract',180,12,volume_mL=20,source_locator='p3 §2.2')
    proc(s,'D01','purification','centrifuge; filter0.22um; dry to brown powder; conditions unspecified',source_locator='p3 §2.2')
    for load in [0,.25,.5,1]:
        f=form('D01','PCH3' if load==0 else f'PCH-CDs{[.25,.5,1].index(load)+1}',s if load else None,
               'PVA/chitosan/hyaluronic acid',cd_loading_pct=load,cd_loading_basis='reported wt% of total substrate',
               processing='6%w/t PVA:1%w/t CS:0.5%w/t HA solutions3:3:1; total20mL; stir12h; centrifuge3000rpm10min; dry40C24h',
               coactive='chitosan',source_locator='p3 §2.2',notes='报告CDs储液0.5/1/2mg/mL各1mL加入20mL成膜液；与0.25/0.5/1wt%换算分母未充分说明。')
        for chem,role,amt,unit in [('PVA','matrix',6,'%w/t stock'),('chitosan','matrix / coactive',1,'%w/t stock'),('hyaluronic acid','matrix',.5,'%w/t stock')]:
            component(f,'D01',chem,role,amt,unit,stage='film',loc='p3 §2.2')
        if load: component(f,'D01','CD stock solution','CD',1,'mL',raw=f'{load*2:g}mg/mL stock',stage='film',loc='p3 §2.2')
        proc(f,'D01','film_forming',
             'add CDs1mL/20mL PCH3 film-forming solution;react24h dark;loaded-film drying not separately specified' if load else 'mix matrix solutions3:3:1;stir12h;3000rpm10min;cast and dry',
             None if load else 40,24,source_locator='p3 §2.2',notes='加载行24h为避光反应时间、温度未明确；对照行40C24h为基膜干燥。')
        if load:
            meas(f,'D01','bacterial_log10_reduction',dict(zip([.25,.5,1],[1.28,1.36,1.45]))[load],
                 'log10 CFU/mL reduction','p9 §3.5.2; p4 §2.6',organism='Escherichia coli',gram='negative',
                 assay_volume_mL=.2,initial_CFU_mL=1e7,contact_min=None,incubation_h=24,temperature_C=37,
                 light='405nm laser',wavelength_nm=405,irradiance_mW_cm2=500,material_context='PVA_CS_HA_film',
                 method='plate colony count',notes='正文未明确该E.coli数值对应10/20/30/40min中哪一时点，contact_min留空。')
        if load==.5:
            meas(f,'D01','bacterial_log10_reduction',None,'log10 CFU/mL reduction','p9 §3.5.2; p4 §2.6',
                 relation='>',value_low=2.20,value_raw='>2.20 log10 CFU/mL',organism='Staphylococcus aureus',gram='positive',
                 contact_min=40,incubation_h=24,assay_volume_mL=.2,initial_CFU_mL=1e7,temperature_C=37,
                 light='405nm laser',wavelength_nm=405,irradiance_mW_cm2=500,method='plate colony count',material_context='PVA_CS_HA_film',
                 notes='不将下界当精确值；体外方法0.5W/cm2与ROS/体内20mW/cm2是不同试验，不相互替换。')
    issue('D01',s,'film_loading_basis','CD储液加入量与报告wt%缺乏明确换算基准；E.coli正文log降低量未绑定时间。','保留原文配方与端点，未知时间留空，不能补为40min。','F24','p3 §2.2; p9 §3.5.2')
    graph('D01','D01-F01 to D01-F04','F24','p10 Fig7','逐膜/菌种/照射时间抗菌曲线','405nm;体外0.5W/cm2;10/20/30/40min')
    route('D01','姜黄提取物',s,'乙醇提取液20mL；180°C12h','复合PCH-CDs2对S.aureus降低>2.20log','PVA/CS/HA膜；405nm40min','仅复合膜定量证据','壳聚糖活性、膜负载和激发条件需分离；不能视为PET碳点标签。')

    # D02: matched positive/negative charge comparison; missing Table S1 is not guessed.
    d02=[]
    for label,pepa in [('PC-CQDs',True),('NC-CQDs',False)]:
        s=syn('D02',label,'citric acid',180,1,method='staged melt pyrolysis',
              precursor_mass_g=3,additive='L-glutathione + PEPA' if pepa else 'L-glutathione',
              additive_volume_mL=10 if pepa else None,reactor_mL=25,storage_C=4,
              source_locator='p2 §2.1',missing_fields='透析MWCO/时长、冻干条件、PEPA分子量',
              notes='3gCA+1gGSH先140C30min；180C阶段PC加10mL PEPA，NC不加；非水热。')
        d02.append(s)
        for chem,amt in [('citric acid',3),('L-glutathione',1)]: component(s,'D02',chem,'precursor',amt,'g',loc='p2 §2.1')
        if pepa: component(s,'D02','polyethene polyamine (PEPA)','cationic passivation precursor',10,'mL',loc='p2 §2.1')
        proc(s,'D02','melting','melt citric acid/GSH',140,.5,source_locator='p2 §2.1')
        proc(s,'D02','CD_synthesis','add PEPA then heat' if pepa else 'heat without PEPA',180,1,source_locator='p2 §2.1')
        proc(s,'D02','purification','acetone precipitation; centrifuge; dialysis; freeze-dry',source_locator='p2 §2.1')
    properties(d02[0],'D02',[('diameter_TEM_nm',2.5,'nm'),('lattice_spacing_nm',.24,'nm'),('zeta_mV',12.9,'mV'),('PLQY_pct',15.24,'%'),('emission_peak_nm',430,'nm'),('XPS_C_pct',73.65,'%'),('XPS_N_pct',15.66,'%'),('XPS_O_pct',10.59,'%'),('XPS_S_pct',.11,'%')],'p3 §3.1')
    meas(d02[1],'D02','zeta_mV',-12.77,'mV','p5 §3.3')
    for org,strain,val in [('Staphylococcus aureus',None,15),('Staphylococcus aureus','MRSA',30),('Escherichia coli','clinical MDR isolate',480),('Pseudomonas aeruginosa','clinical MDR isolate',480)]:
        meas(d02[0],'D02','MIC_ug_mL',val,'ug/mL','p5 §3.2; p2 §2.3',organism=org,strain=strain,
             gram='positive' if 'aureus' in org else 'negative',method='broth dilution; no visible growth',
             initial_CFU_mL=7.5e5,temperature_C=35,medium='Mueller-Hinton broth',incubation_h=None,
             notes='培养16-20h范围未取中点；未指定光激活，light未知；SI TableS1未提供，不能补齐其他菌的MIC。')
    for org,strain,val,dose in [('Staphylococcus aureus',None,99.21,15),('Staphylococcus aureus','MRSA',99.92,30),('Escherichia coli',None,93.68,None),('Pseudomonas aeruginosa',None,92.09,None),('Escherichia coli',None,98.42,None),('Pseudomonas aeruginosa',None,94.47,None)]:
        factor='2xMIC' if val in [98.42,94.47] else '1xMIC'
        meas(d02[0],'D02','bacterial_killing_pct',val,'%','p5 §3.2',organism=org,strain=strain,
             dose_ug_mL=dose,dose_basis=f'PC-CQDs {factor}',contact_min=240,method='plate colony count',
             notes='E.coli/P.aeruginosa普通菌株MIC仅在缺失SI中；不借用临床MDR的480ug/mL。')
    for org in ['Staphylococcus aureus','Escherichia coli','Pseudomonas aeruginosa']:
        meas(d02[1],'D02','MIC_ug_mL',None,'ug/mL','p5 §3.3',relation='>',value_low=500,value_raw='MIC>500ug/mL, all selected bacteria',organism=org,
             method='broth dilution',notes='正文对所有测试菌的共同下界；非500精确值；非独立合成批次。')
    issue('D02',d02[0],'missing_supporting_information','TableS1与FigS5未随新增文件提供，普通E.coli/P.aeruginosa的MIC无正文明确值。','仅记录正文明确MIC；4h杀菌率保留MIC倍数，剂量未知留空。','F25','p5 §3.2')
    route('D02','柠檬酸 + 谷胱甘肽 + PEPA',d02[0],'140°C30min后180°C1h；PEPA10mL','S.aureus MIC15ug/mL；MRSA30ug/mL；NC对照MIC>500','肉汤稀释；未报告光激活','有游离CD及不加PEPA比较','支持阳离子化假设；不加PEPA还会改变粒径/组成，不能仅按zeta作因果归因。')

    # D03: read the appended 2025 corrigendum, distinguish concentration/time series.
    d03=[]
    for temp in [180,200,220,240]:
        s=syn('D03',f'ST-JHCQDs-{temp}','turmeric ethanolic extract',temp,10,method='solvothermal',reactor_mL=25,filter_um=.22,
              source_locator='p3 §§2.2-2.3',missing_fields='碳点绝对前驱体质量、产率、透析未报告',
              notes='共享提取2g姜黄/30mL乙醇；取20mL上清反应，不能记每釜投料2g；240C未报告相同抗菌系列。')
        d03.append(s); component(s,'D03','turmeric ethanolic extract','precursor solution',20,'mL',loc='p3 §2.3')
        proc(s,'D03','CD_synthesis','solvothermal',temp,10,volume_mL=20,source_locator='p3 §2.3')
        proc(s,'D03','purification','centrifuge; filter0.22um; rotary evaporation; ethyl acetate/petroleum ether precipitation',source_locator='p3 §2.3')
        proc(s,'D03','drying','oven',60,None,source_locator='p3 §2.3')
    for chem,amt,unit in [('turmeric powder',2,'g'),('ethanol',30,'mL')]: component('D03-PRE','D03',chem,'shared extraction',amt,unit,stage='extraction',loc='p3 §2.2')
    proc('D03-PRE','D03','extraction','dry turmeric60C; ethanol ultrasound30min;8000rpm10min;filter0.22um',time=.5,source_locator='p3 §2.2')
    properties(d03[0],'D03',[('diameter_TEM_nm',10.7,'nm'),('zeta_mV',-17.5,'mV')],'p7 §3.1; zeta in0.9%NaCl')
    for idx in range(3):
        for org,dose,early,late in [('Staphylococcus aureus',5,[87,66,40][idx],[99.9,99,91][idx]),('Escherichia coli',50,[51,58,21][idx],[99.9,99,70][idx])]:
            for t,val in [(5,early),(40,late)]:
                meas(d03[idx],'D03','bacterial_inactivation_pct',val,'%','p10 §3.3.2; p4 §2.5.3',organism=org,
                     gram='positive' if 'aureus' in org else 'negative',dose_ug_mL=dose,dose_basis='CD; final concentration',contact_min=t,
                     incubation_h=24,temperature_C=37,initial_OD600=.5,medium='0.9%NaCl; LB agar plating',light='blue',
                     wavelength_nm=405,irradiance_mW_cm2=20,n=3,method='plate colony count',
                     notes='时间系列；PDF中µg/mL被抽取器误读mg/mL，已目视p4/p10核对；预孵育30min另计。')
    meas(d03[0],'D03','bacterial_inactivation_pct',99.9,'%','p10 §3.3.2',organism='Staphylococcus aureus',dose_ug_mL=5,
         contact_min=20,incubation_h=24,light='blue',wavelength_nm=405,irradiance_mW_cm2=20,method='plate colony count',notes='正文明确20min端点。')
    for idx,org,dose,val in [(0,'Staphylococcus aureus',5,55),(0,'Escherichia coli',50,26),(1,'Escherichia coli',50,38),(2,'Escherichia coli',50,33)]:
        meas(d03[idx],'D03','bacterial_inactivation_pct',val,'%','p10 §3.3.1; p20 corrigendum',organism=org,dose_ug_mL=dose,
             contact_min=40,light='dark',method='plate colony count',data_status='conflict',
             notes='剂量系列对照；方法p4写µM，图6和正文写µg/mL；按正文保留量，核对原始实验前不作普通回归。照射组时间按勘误40min。')
    issue('D03','D03-all','corrigendum','随PDF附2025勘误：Fig6c/d、Fig7c/d图片误用；220误标240；§2.5.2照射30min应40min。','采用勘误40min，保留修订DOI10.1016/j.jmrt.2025.03.171；不使用错误图片反推数值。','F26','p19-22 appended correction; p20 correction text')
    issue('D03','D03-all','dose_units','§2.5.2写0.5/5/50µM，而Fig6与§3.3.1写µg/mL；§2.5.3时间系列明确µg/mL。','时间系列采用已目视确认µg/mL；剂量系列标冲突；不把PDF抽取的mg误作毫克。','F26','p4 §§2.5.2-2.5.3; p10')
    graph('D03','D03-S01 to D03-S03','F26','p10-11 Fig6-7; p21-22 corrected panels','其余剂量/时间端点','405nm20mW/cm2；0.5/5/50ug/mL；5/10/20/40min','先解决剂量系列µM/µg冲突，使用勘误替换图片；不重复记录正文已给端点。')
    route('D03','姜黄提取物保留光敏官能团',d03[0],'乙醇萃取20mL；180°C10h','S.aureus5ug/mL20min失活99.9%；温度系列180/200/220°C','405nm20mW/cm2；未加外部光敏剂','有游离CD数值及制备温度比较','活性随碳化程度变化；需区分保留天然分子与碳核贡献，不能从植物路线推定PET有效。')

    # D04: post-synthesis zinc complex is a separate entity.
    s=syn('D04','MC-CDs','methylene blue',180,8,water_mL=25,precursor_mass_g=.37,additive='cetyltrimethylammonium chloride',
          additive_mass_g=.32,reactor_mL=50,filter_um=.22,dialysis_h=120,freeze_dry_C=-60,
          source_file_id='F28',source_locator='SI p3 §1.3',missing_fields='MWCO原文500-1000Da范围，不取中点',notes='透析500-1000Da5days；原文vacuum dried at-60C；非推测初始pH。')
    for chem,amt,unit in [('methylene blue',.37,'g'),('CTAC',.32,'g'),('water',25,'mL')]: component(s,'D04',chem,'precursor/solvent',amt,unit,source='F28',loc='SI p3 §1.3')
    proc(s,'D04','CD_synthesis','ultrasound; hydrothermal',180,8,source_file_id='F28',source_locator='SI p3 §1.3')
    proc(s,'D04','purification','filter0.22um; dialysis500-1000Da5days; vacuum dry-60C',time=120,source_file_id='F28',source_locator='SI p3 §1.3')
    properties(s,'D04',[('diameter_TEM_nm',1.58,'nm'),('lattice_spacing_nm',.21,'nm'),('Raman_ID_IG',.95,'ratio')],'p2 §2')
    properties(s,'D04',[('XPS_C_pct',84.64,'%'),('XPS_N_pct',6.74,'%'),('XPS_O_pct',6.08,'%'),('XPS_S_pct',1.48,'%'),('XPS_Cl_pct',1.06,'%')],'p3 §2')
    properties(s,'D04',[('PLQY_pct',12.33,'%'),('singlet_oxygen_QY_pct',34.97,'%'),('PL_lifetime_ns',.45,'ns'),('emission_peak_nm',663,'nm')],'p5 §2')
    meas(s,'D04','zeta_mV',17.1,'mV','p7; p10 Fig6b')
    z=form('D04','Zn@MC-CDs',s,'none',coactive='post-complexed Zn2+',processing='MC-CDs1mg/mL + Zn2+1mM;25C24h;dialysis500-1000Da36h;lyophilize',source_file_id='F28',source_locator='SI p3 §1.3',notes='后配位金属体系；不按无金属CD本体归因。')
    component(z,'D04','MC-CDs','CD',1,'mg/mL',stage='post_complexation',source='F28',loc='SI p3 §1.3')
    component(z,'D04','Zn2+','metal coactive',1,'mM',stage='post_complexation',source='F28',loc='SI p3 §1.3')
    proc(z,'D04','post_complexation','stir then dialysis36h MWCO500-1000Da',25,24,source_file_id='F28',source_locator='SI p3 §1.3')
    properties(z,'D04',[('diameter_TEM_nm',2.14,'nm'),('XPS_Zn_pct',2.03,'%'),('XPS_C_pct',71.44,'%'),('XPS_N_pct',8.99,'%'),('XPS_O_pct',14.10,'%')],'p9')
    meas(z,'D04','zeta_mV',19.16,'mV','p10 Fig6b')
    for org,strain,dose,killing,mbc,dark,zkill in [('Escherichia coli','ATCC25922',14,96.83,56,82.39,98.14),('Staphylococcus aureus','ATCC6538',18,94.44,72,83.84,98.64)]:
        base=dict(organism=org,strain=strain,contact_min=10,incubation_h=24,temperature_C=37,light='red laser',wavelength_nm=660,irradiance_mW_cm2=100,n=3)
        meas(s,'D04','bacterial_inactivation_pct',killing,'%','p5; SI p5 §1.5.3',dose_ug_mL=dose,method='OD600 growth inhibition',data_status='conflict',**base,notes='正文称inactivation但此百分数来自LB液体OD；SI EqS2比率公式可产生>100%疑似排版错误，暂不作普通回归。')
        meas(s,'D04','MIC_ug_mL',dose,'ug/mL','p6',method='authors MIC designation under photoactivation',**base,notes='作者将14/18ug/mL称MIC；与96.83/94.44%OD抑制同处，非标准无可见生长阈值需核查。',regression_eligible=0)
        meas(s,'D04','MBC_ug_mL',mbc,'ug/mL','p6; FigS9 referenced',method='authors MBC,99.9% kill',**base,notes='主文明确MBC；SI图S9未另读柱高。')
        for light,val in [('dark',dark),('red laser',zkill)]:
            meas(z,'D04','bacterial_inactivation_pct',val,'%','p10; SI p5 §1.5.3',organism=org,strain=strain,dose_ug_mL=dose,
                 dose_basis='Zn@MC-CD complex total',contact_min=10 if light!='dark' else None,incubation_h=24,light=light,
                 wavelength_nm=660 if light!='dark' else None,irradiance_mW_cm2=100 if light!='dark' else None,
                 material_context='CD_Zn_complex',method='OD600 growth inhibition',data_status='conflict',
                 notes='保留Zn协同层级；暗组无明确等时10min，不补时间；SI EqS2定义待核查。')
    issue('D04',s,'OD600_ratio/MIC_definition','SI EqS2写1-(ODtreated-ODcontrol)/ODcontrol；正文MIC对应的OD抑制未达100%。','百分数与MIC定义保留并排除普通回归，先确认公式/阈值；MBC与OD百分数不混合。','F28/F29','SI p5 EqS2; main p5-6')
    issue('D04',z,'PL_lifetime_unit','正文Zn@MC-CDs寿命写0.18nm，时间单位不成立。','不填PL_lifetime_ns，不擅改nm为ns。','F29','p9')
    graph('D04',s,'F29/F28','Fig4-6; SI FigS9,S19','浓度-光暗及生物膜曲线','MC-CD与Zn后配位分层；先核实OD公式')
    route('D04','亚甲基蓝 + CTAC',s,'0.37gMB+0.32gCTAC/25mL；180°C8h；透析5天','MBC：E.coli56、S.aureus72ug/mL；OD百分数定义待核查','660nm100mW/cm2、10min','游离自封端CD光动力；Zn后配位另列','前驱体自身具光敏/抗菌活性；残留及吸附分子需对照，不能把Zn增强归因CD碳核。')

    # D05: CDP concentration is PpIX-equivalent, not carbon-dot mass.
    s=syn('D05','BCDs','purple rice lixivium',140,4,water_mL=None,dialysis_MWCO_Da=1000,storage_C=4,
          source_locator='p14 ExperimentalSection',missing_fields='7mL浸提液实际碳质量、反应容器/釜容量',
          notes='50g紫米/200mL水250W超声3min为共享浸提；取7mL；每3h换水4次。')
    for chem,amt,unit in [('purple rice',50,'g'),('water',200,'mL')]: component('D05-PRE','D05',chem,'shared extraction',amt,unit,stage='extraction',loc='p14')
    component(s,'D05','purple rice lixivium','precursor solution',7,'mL',loc='p14')
    proc(s,'D05','CD_synthesis','heat purple rice lixivium',140,4,volume_mL=7,source_locator='p14')
    proc(s,'D05','purification','dialysis1000Da; replace water every3h four times;4C storage or lyophilize',source_locator='p14')
    properties(s,'D05',[('XPS_C_pct',60.08,'%'),('XPS_N_pct',2.62,'%'),('XPS_O_pct',36.97,'%'),('XPS_S_pct',.33,'%')],'p3 Fig2f')
    cdf=form('D05','CDFs',s,'none',coactive='FITC fluorophore',processing='BCDs5mg + FITC100ug;1mL10mM carbonate pH9.5;room-temperature overnight;dialysis1000Da',source_locator='p14',notes='荧光成像实体，无抗菌结果不能标0。')
    cdps=form('D05','CDPs',s,'none',coactive='protoporphyrin IX (PpIX)',processing='PpIX1mg+EDC.HCl1.4mg+NHS2mg/100uLDMSO4h;BCDs10mg/2mLPBS overnight;dialysis3000Da24h',source_locator='p14',notes='CDPs测试浓度按PpIX计，不能当CD净质量。')
    for e,chem,amt,unit in [(cdf,'BCDs',5,'mg'),(cdf,'FITC',.1,'mg'),(cdps,'BCDs',10,'mg'),(cdps,'PpIX',1,'mg'),(cdps,'EDC.HCl',1.4,'mg'),(cdps,'NHS',2,'mg')]: component(e,'D05',chem,'post-functionalization',amt,unit,stage='functionalization',loc='p14')
    for ep,rel in [('MIC50_ug_mL','approximately'),('MBC_ug_mL','=')]:
        meas(cdps,'D05',ep,5,'ug/mL','p8 §2.3',organism='Staphylococcus aureus',relation=rel,
             dose_basis='PpIX equivalent in CDPs',light='white',material_context='CD_photosensitizer_conjugate',
             method='MIC50:50% growth inhibition; MBC:survival<=0.1%',notes='激发光强/时长在未提供SI，未知留空；MIC50与MIC分开。')
    graph('D05',cdps,'F31','p9 Fig5; SI methods/S16 absent','CDP/PpIX剂量生存率及光照完整协议','PpIX equivalent concentrations','仅主文明确MIC50约5和MBC5；先补SI，不从图估读。')
    route('D05','紫米碳点 + 后接枝PpIX',s,'紫米浸提液140°C4h；随后EDC/NHS偶联PpIX','CDP光动力MBC5ug/mL（按PpIX）','白光；外接光敏剂','载体/光敏剂复合贡献','不能作为未接枝BCDs或PET碳点自抗菌标签。')

    # D06: nominal dose versus mixture dose is explicitly ambiguous.
    s=syn('D06','BAPTCDs','D-glutamic acid',200,3,method='solvothermal in aqueous HCl',precursor_mass_g=.025,
          additive='o-phenylenediamine',additive_mass_g=.05,additive_precursor_mass_ratio=2,dialysis_MWCO_Da=500,freeze_dry_h=24,
          centrifuge_rpm=3000,centrifuge_min=10,source_locator='p2 Synthesis of Carbon Dots',missing_fields='透析overnight未量化、初始pH/釜容量',notes='25mL1M HCl水溶液不是纯水25mL；保留D型前驱体。')
    for chem,amt,unit in [('D-glutamic acid',25,'mg'),('o-phenylenediamine',50,'mg'),('HCl aqueous solution1M',25,'mL')]: component(s,'D06',chem,'precursor/acid solvent',amt,unit,loc='p2')
    proc(s,'D06','CD_synthesis','solvothermal in1M HCl25mL',200,3,source_locator='p2')
    proc(s,'D06','purification','centrifuge3000rpm10min;dialysis500Da overnight;freeze-dry24h',source_locator='p2')
    properties(s,'D06',[('diameter_TEM_nm',3,'nm'),('PLQY_pct',38,'%'),('XPS_C_pct',57.2,'%'),('XPS_N_pct',18.4,'%'),('XPS_O_pct',24.4,'%')],'p5 Results')
    for org,strain,dark in [('Escherichia coli','ATCC700926',80.33),('Staphylococcus aureus','ATCC29213',89.27)]:
        meas(s,'D06','bacterial_killing_pct',dark,'%','p7 Antibacterial Activity; p4 protocol',organism=org,strain=strain,light='dark',
             dose_basis='authors nominal200ug/mL;400uL stock+100uL bacteria implies160ug/mL',contact_min=180,
             incubation_h=16,temperature_C=37,method='plate colony count',data_status='conflict',notes='3h预孵育；剂量名义/最终值冲突，标准剂量留空。')
        meas(s,'D06','bacterial_survival_pct',3.67 if 'coli' in org else 0,'%','p7; p4 protocol',organism=org,strain=strain,
             dose_basis='nominal200ug/mL; mixture implies160ug/mL',contact_min=10,incubation_h=16,temperature_C=37,
             light='NIR',wavelength_nm=808,irradiance_mW_cm2=1500,method='plate colony count',relation='=' if 'coli' in org else 'reported_zero',
             data_status='conflict',notes='照射前3h另计；S.aureus全杀未给检出限，0存活不直接换100。')
    issue('D06',s,'dose_ug_mL','方法400uL200ug/mL CD+100uL菌液理论最终160ug/mL，结果与图仍称200ug/mL。','原文名义200保留dose_basis，标准剂量空，杀菌数值标conflict待核实。','F36','p4 Antibacterial Activity; p7 Fig7')
    route('D06','D-谷氨酸 + 邻苯二胺',s,'25mgD-Glu+50mgo-PDA/25mL1MHCl；200°C3h','暗组E.coli80.33%、S.aureus89.27%；剂量定义待核查','预孵育3h；NIR808nm另组','有游离CD光暗试验，当前剂量有歧义','MurD竞争抑制为作者机制解释，缺直接酶动力学证明；需配套热对照。')

    # D07: PHMG is already antimicrobial; causal attribution needs precursor control.
    s=syn('D07','DG-CDs','citric acid',150,6,precursor_mass_g=.4,additive='dextran Mw20000 + PHMG',water_mL=20,
          reactor_mL=50,filter_um=.22,dialysis_h=48,source_locator='p9 §2.3',missing_fields='MWCO500-1000Da范围、冻干条件、产率',notes='0.4gCA+0.4gDEX+50mgPHMG；不是DEX后包覆。')
    for chem,amt,unit in [('citric acid',.4,'g'),('dextran Mw20000',.4,'g'),('PHMG',.05,'g'),('water',20,'mL')]: component(s,'D07',chem,'precursor/solvent',amt,unit,loc='p9 §2.3')
    proc(s,'D07','CD_synthesis','hydrothermal',150,6,source_locator='p9 §2.3')
    proc(s,'D07','purification','filter0.22um;dialysis500-1000Da48h;freeze-dry',time=48,source_locator='p9 §2.3')
    properties(s,'D07',[('diameter_TEM_nm',3.84,'nm'),('lattice_spacing_nm',.21,'nm'),('zeta_mV',22.6,'mV'),('emission_peak_nm',450,'nm')],'p18 §3.1')
    properties(s,'D07',[('XPS_C_pct',59.64,'%'),('XPS_N_pct',11.31,'%'),('XPS_O_pct',29.05,'%')],'p20 §3.1')
    for org,strain,val in [('Staphylococcus aureus','ATCC6538',5),('Staphylococcus aureus','ATCC43300 MRSA',5),('Staphylococcus epidermidis','ATCC12228',1.25)]:
        meas(s,'D07','MIC_ug_mL',val,'ug/mL','p23 §3.2; p10 §2.5',organism=org,strain=strain,gram='positive',
             method='broth dilution; no visible growth',initial_CFU_mL=7.5e5,medium='Mueller-Hinton broth',incubation_h=24,
             notes='菌浓度由1mL1.5e6+1mL培养液推得；未指定光激活，light留空；S2其余菌MIC未在正文列明。')
    for strain in ['ATCC6538','ATCC43300 MRSA']:
        meas(s,'D07','bacterial_colony_observation',None,None,'p23 §3.2; p11 §2.7',organism='Staphylococcus aureus',strain=strain,
             dose_ug_mL=10,method='plate colony count',data_status='qualitative',evidence_text='no bacterial colonies',
             notes='接触时长未明确，观察不强换100%/MBC。')
    issue('D07',s,'PHMG_control_and_missing_SI','PHMG本身为抗菌聚合物；SI TableS2、系列配方与所有菌株MIC未提供。','标明含胍基前驱体；不声称抗菌全部源自碳核；仅记录正文3个MIC。','F37','p9 §2.3; p23 §3.2')
    route('D07','柠檬酸 + 葡聚糖 + PHMG',s,'0.4gCA+0.4gDEX+0.05gPHMG/20mL；150°C6h','S.aureus/MRSA MIC5；S.epidermidis1.25ug/mL','肉汤24h；未指定激活光','有游离胍基CD数值MIC','PHMG已有独立抗菌作用；PET替代碳源后胍基是否保留需重新验证。')

    # D08: units visually checked: ug/mL,250uM; MIC50 not MIC.
    d08=[]
    for label,co in [('Co-Lvx-CDs',True),('Lvx-CDs',False)]:
        s=syn('D08',label,'levofloxacin',180,8,precursor_mass_g=.361,water_mL=15,additive='vitamin B12' if co else None,
              additive_mass_g=.271 if co else None,reactor_mL=25,centrifuge_rpm=8000,centrifuge_min=10,filter_um=.22,
              dialysis_MWCO_Da=1000,dialysis_h=24,source_locator='p3 synthesis',missing_fields='初始pH、冻干条件',notes='含抗生素来源前驱体；Co来源B12，Co掺杂与抗生素残存不能混为纯碳贡献。')
        d08.append(s)
        component(s,'D08','levofloxacin','antibiotic precursor',.361,'g',loc='p3')
        if co: component(s,'D08','vitamin B12','Co precursor',.271,'g',loc='p3')
        component(s,'D08','water','solvent',15,'mL',loc='p3')
        proc(s,'D08','CD_synthesis','hydrothermal',180,8,source_locator='p3')
        proc(s,'D08','purification','8000rpm10min;filter0.22um;dialysis1000Da24h,water every4h;lyophilize',time=24,source_locator='p3')
    properties(d08[0],'D08',[('diameter_TEM_nm',3.1,'nm'),('lattice_spacing_nm',.32,'nm'),('mass_yield_pct',64,'%'),('Raman_ID_IG',1.02,'ratio'),('XPS_C_pct',70.34,'%'),('XPS_O_pct',16.44,'%'),('XPS_N_pct',10.29,'%'),('XPS_F_pct',2.06,'%'),('XPS_Co_pct',.87,'%')],'p4 Results; size/yield approximately')
    meas(d08[0],'D08','PLQY_pct',21.8,'%','p3 Introduction; absolute QY')
    meas(d08[1],'D08','diameter_TEM_nm',3,'nm','p4 Results',relation='approximately')
    for org,strain,val in [('Staphylococcus aureus','CMCC(B)26003',.938),('Escherichia coli','ATCC25922',1.077)]:
        meas(d08[0],'D08','MIC50_ug_mL',val,'ug/mL','p7; p4 assay',organism=org,strain=strain,
             initial_CFU_mL=1e6,incubation_h=24,medium='LB',method='OD/turbidimetry; MIC50',notes='µg/mL已目视确认；MIC50独立端点。')
    for org,surv,h2o2,status in [('Staphylococcus aureus',.9,.25,'reported'),('Escherichia coli',10.91,0,'reported')]:
        meas(d08[0],'D08','bacterial_survival_pct',surv,'%','p7-8 Fig5; p4 assay',organism=org,dose_ug_mL=50,
             contact_min=30,incubation_h=24,temperature_C=37,initial_CFU_mL=1e6,H2O2_mM=h2o2,medium='LB',
             method='plate colony count',material_context='free_CD_with_H2O2' if h2o2 else 'free_CD',
             notes='H2O2原文250µM=0.25mM；50µg/mL单位已目视p7确认；不补未明确的光状态。')
    graph('D08','D08-S01 to D08-S02','F38','p7-9 Fig5; missing ESI S13-16','配对加/不加H2O2抗菌率及非掺Co对照','50ug/mL;30min;250uMH2O2','正文E.coli近99.9%为近似表述，未读图不当精确99.9；需补ESI。')
    route('D08','左氧氟沙星 + 维生素B12',d08[0],'361mgLvx+271mgB12/15mL；180°C8h','MIC50约0.938/1.077ug/mL；S.aureus加H2O2存活0.9%','部分端点需0.25mMH2O2','抗生素来源含Co CD；H2O2另分','MIC50不能等同MIC；不是PET替代抗生素碳源后的已验证路线。')

    # D09: intrinsic CD MIC and film response are different material levels.
    s=syn('D09','L-CDs','L-lysine',None,4/60,method='microwave pyrolysis',precursor_mass_g=1,water_mL=5,
          sonication_min=30,filter_um=.22,dialysis_MWCO_Da=1000,dialysis_h=24,source_locator='p7 §2.2',
          missing_fields='微波温度、产率、冻干条件',notes='750W4min；冷却后另加50mL水不合并为初始55mL。')
    component(s,'D09','L-lysine','precursor',1,'g',loc='p7 §2.2'); component(s,'D09','water','initial solvent',5,'mL',loc='p7 §2.2')
    component(s,'D09','water','postreaction dilution',50,'mL',stage='purification',loc='p7 §2.2')
    proc(s,'D09','CD_synthesis','microwave750W',time=4/60,source_locator='p7 §2.2')
    proc(s,'D09','purification','add50mLwater;ultrasound30min;filter0.22um;dialysis1000Da24h,waterevery8h',time=24,source_locator='p7 §2.2')
    properties(s,'D09',[('XPS_C_pct',69.24,'%'),('XPS_O_pct',25.50,'%'),('XPS_N_pct',5.26,'%')],'p13 §3.1')
    for ph,val in [(7.4,3.48),(6.5,9.06),(5.3,17.17)]: meas(s,'D09','zeta_mV',val,'mV','p23 §3.5; FigS2 cited',pH=ph)
    for org,strain,val in [('Escherichia coli','ATCC25922',21.875),('Staphylococcus aureus','CMCC26003',10.93)]:
        meas(s,'D09','MIC_ug_mL',val,'ug/mL','p21 §3.5; p9 §2.6',organism=org,strain=strain,
             method='turbidimetry',notes='SI完整培养条件未提供；正文数值保留，未知剂量梯度、菌量、培养时长不猜。')
    film_ids=[]
    for load in [0,2.5,5,7.5,10]:
        f=form('D09','CS' if not load else f'CS/{load:g}%L-CDs',s if load else None,'chitosan',cd_loading_pct=load,
               cd_loading_basis='ambiguous: text mass fractions relative CS but unit vol%',coactive='chitosan',matrix_mass_g=4.5,
               processing='4.5gCS/150mL1wt%acetic acid;25C20rpm2h;glycerol1wt%2h;CDs mix1h+sonicate10min;cast25C36h',source_locator='p8 §2.3',
               notes='2.5/5/7.5/10是原文vol%标签，绝不转换CD质量百分数。')
        film_ids.append(f)
        component(f,'D09','chitosan','matrix/coactive',4.5,'g',stage='film',loc='p8 §2.3')
        component(f,'D09','glycerol','plasticizer',1,'wt%',basis='not clearly defined',stage='film',loc='p8 §2.3')
        if load: component(f,'D09','L-CDs stock','CD',load,'vol%',basis='ambiguous original wording',stage='film',loc='p8 §2.3')
        proc(f,'D09','drying','cast on glass',25,36,source_locator='p8 §2.3')
    meas(film_ids[0],'D09','bacterial_inhibition_pct',3.8,'%','p22 §3.5; p9-10 assay',organism='Escherichia coli',contact_min=30,
         incubation_h=24,temperature_C=37,assay_volume_mL=.2,material_context='CS_film_control',method='plate colony count',notes='纯CS对照，不是失败CD配方。')
    issue('D09','D09-all','film_loading_and_year','§2.3写mass fractions relative toCS却使用vol%；预印本封面推荐引文2024但DOI/接受日期为2025。','保留vol%及基准冲突；来源年按2025接受版本，不猜最终卷期；35.6/99.9%未分配明确配方不自动绑定10%。','F39','p1 cover; p8 §2.3; p22 §3.5')
    graph('D09','D09-F01 to D09-F05','F39','p22 Fig8; SI absent','各膜逐菌定量及游离CD MIC完整协议','1x1cm膜；200uL菌液；37C30min','正文35.6/99.9%未明确对应加载水平，留在证据摘要，读清图后再建行。')
    route('D09','L-赖氨酸',s,'1g/5mL水；750W微波4min；透析1000Da24h','游离CD MIC：E.coli21.875、S.aureus10.93ug/mL','完整MIC方法在未提供SI','游离CD MIC及pH相关zeta','支持氨基前驱体假设；PET主碳源可能改变碳化产物，需实际PET对照。')

    # D10: report zero colony observation, not an invented log-kill value.
    s=syn('D10','citric-acid C-DOTS','citric acid',None,8/60,method='open microwave',precursor_mass_g=100,water_mL=100,
          dialysis_MWCO_Da=1300,dialysis_h=48,source_locator='p3 Synthesis',missing_fields='微波实际瓦数/温度、热风干燥条件',notes='原文100g/100mL按原值保留；high potency未量化瓦数。')
    component(s,'D10','citric acid','precursor',100,'g',loc='p3');component(s,'D10','water','solvent',100,'mL',loc='p3')
    proc(s,'D10','CD_synthesis','domestic microwave high potency;open atmosphere',time=8/60,source_locator='p3')
    proc(s,'D10','purification','dialysis1300Da2days;hot-air oven drying',time=48,source_locator='p3')
    meas(s,'D10','diameter_TEM_nm',3.81,'nm','p4 Characterization')
    meas(s,'D10','lattice_spacing_nm',.35,'nm','p4',uncertainty=.02,uncertainty_type='not_specified')
    meas(s,'D10','emission_peak_nm',450,'nm','p7',relation='approximately')
    for context,dose in [('free_CD',6900),('CD_biofilm_assay',None)]:
        meas(s,'D10','bacterial_colony_observation',None,None,'p7 Results; p3-4 methods',organism='Staphylococcus aureus',strain='ATCC25923',
             dose_ug_mL=dose,dose_basis='CD6.9mg/mL' if dose else 'biofilm13.8mg/mL results vs13.8mg/L methods',
             contact_min=16.7,incubation_h=24,temperature_C=37,light='blue LED',wavelength_nm=450,irradiance_mW_cm2=40,
             medium='PBS;BHI agar',material_context=context,data_status='qualitative',method='plate colony count',evidence_text='complete elimination at40J/cm2',
             notes='预孵育40min；零检出不换100%或无限log；方法光照16.7min为原文值。')
    issue('D10',s,'biofilm_dose_units','方法p4写3.45/6.9/13.8mg/L，结果/图6与摘要写mg/mL。','生物膜标准剂量留空，不将1000倍差异自行纠正；悬浮菌6.9mg/mL在方法/结果一致。','F40','p4; p7-8 Fig6')
    graph('D10',s,'F40','p8 Fig6; p9 Fig7','悬浮菌/生物膜逐浓度-光剂量CFU','450nm40mW/cm2;0/20/40/60J/cm2','保留两种菌状态；先解决mg/L与mg/mL差异；不估读检出限。')
    route('D10','柠檬酸单前驱体',s,'100g/100mL水；微波high potency8min','悬浮S.aureus6.9mg/mL、40J/cm2未检出菌落','450nm40mW/cm2；预孵育40min','游离CD光激活定性零检出','剂量很高且需光；不能把未检出等同精确100%或外推PET。')

    # D11: MIC values exceed the stated tested range; keep all six groups separate.
    s=syn('D11','RKG-CDs','red Korean ginseng aqueous root extract',None,14/60,method='cyclic microwave',dialysis_MWCO_Da=3500,
          source_locator='p2 §2.2',missing_fields='提取质量/体积、微波温度、透析时长、冻干条件',
          notes='700W2450MHz；7个2min加热周期，中间冷却2min；14min为总通电时间，不含冷却。')
    component(s,'D11','red Korean ginseng root aqueous extract','precursor solution',raw='mass/volume not given',loc='p2 §2.2')
    proc(s,'D11','CD_synthesis','700W2450MHz;2min heating x7cycles;2min cooling intervals',time=14/60,source_locator='p2 §2.2',notes='不把14min当包括冷却的总耗时。')
    proc(s,'D11','purification','dialysis3500Da;lyophilize',source_locator='p2 §2.2')
    meas(s,'D11','diameter_TEM_nm',None,'nm','p1 abstract',relation='range',value_low=1,value_high=4,data_status='reported_range')
    meas(s,'D11','PLQY_pct',8,'%','p10 Discussion/Table1')
    rut=form('D11','CDs-RUT',s,'none',coactive='rutin',processing='CDs aqueous:RUT inDMSO1:1 mass;room-temperature overnight;dialysis24h;lyophilize',source_locator='p2 §2.3',notes='投料1:1非实际装载率；实测DLC12.7%。')
    for chem in ['RKG-CDs','rutin']: component(rut,'D11',chem,'CD / drug',1,'part mass',basis='CD:RUT1:1',stage='loading',loc='p2 §2.3')
    proc(rut,'D11','drug_loading','stir overnight room-temperature;dialysis24h;lyophilize',source_locator='p2 §2.3')
    meas(rut,'D11','drug_loading_content_pct',12.7,'%','p1 abstract; p2 definition',material_context='CD_rutin_nanohybrid',method='TGA/UV-vis',notes='药物质量/纳米颗粒质量。')
    for org,vals in [('Staphylococcus aureus',[(540,170),(260,100)]),('Escherichia coli',[(550,180),(270,150)])]:
        for light,(cdval,hybridval) in zip(['dark','visible LED'],vals):
            for entity,val,context in [(s,cdval,'free_CD'),(rut,hybridval,'CD_rutin_nanohybrid')]:
                meas(entity,'D11','MIC_ug_mL',val,'ug/mL','p8 §3.10; p3 §2.15',organism=org,light=light,
                     lamp_power_W=36 if light!='dark' else None,incubation_h=18,temperature_C=37,medium='LB',
                     material_context=context,method='growth assay; authors MIC',data_status='conflict',value_raw=f'{val/1000:g}mg/mL',
                     notes='原文方法0-100ug/mL，正文MIC100-550ug/mL；MIC测定/外推定义未充分报告，保留换算但排除普通回归。灯15cm，无样品处功率密度。')
    issue('D11',s,'MIC_range','方法只写0-100ug/mL，而MIC正文最高0.55mg/mL=550ug/mL。','原文MIC明确值保留但标conflict；不将0.54mg/mL误作0.54ug/mL，不猜额外剂量实验。','F42','p3 §2.15; p8 §3.10')
    graph('D11',s,'F42','p7 Fig5; p8 Fig6','光暗生长/ROS/膜完整性曲线','CD、RUT、CD-RUT三组；18h；36WLED','先补MIC算法/剂量范围；不给未标数字的曲线填点值。')
    route('D11','红参水提碳点（芦丁后加载另列）',s,'700W微波7x2min；3500Da透析','游离CD光/暗MIC转述260-550ug/mL，范围与方法冲突','36WLED18h；功率密度未知','有游离CD试验，但MIC定义待核实','抗氧化/光生ROS依条件改变；芦丁增效不能归因CD本体，冲突标签不直接训练。')

    # D12/D13: mechanism/synthesis controls, no measured antibacterial label.
    s=syn('D12','dual-emission SOD-like CDs','glutathione',None,3/60,method='microwave',precursor_mass_g=.5,additive='formamide solvent',
          sonication_min=3,dialysis_MWCO_Da=3500,dialysis_h=24,source_locator='p14 Preparation of CDs',
          missing_fields='微波温度、产率、冻干条件',notes='0.5gGSH/20mLformamide；100W3min；SOD抗氧化作物研究，不是抗菌阴性样本。')
    component(s,'D12','glutathione','precursor',.5,'g',loc='p14');component(s,'D12','formamide','solvent',20,'mL',loc='p14')
    proc(s,'D12','CD_synthesis','sonicate3min then microwave100W3min',time=3/60,source_locator='p14')
    proc(s,'D12','purification','dialysis3500Da24h;freeze-dry',time=24,source_locator='p14')
    s=syn('D13','C@C3-30V-24H','graphite rods99.99%',None,24,method='electrochemical exfoliation',filter_um=.22,centrifuge_rpm=8000,
          centrifuge_min=40,dialysis_MWCO_Da=300,dialysis_h=48,source_locator='p2 §2.2',missing_fields='电极消耗质量、反应温度',
          notes='3mMHCl500mL；电极间6cm；30V24h为明示最优样品；不把多因素水平擅自展开全部27配方。无抗菌试验。')
    component(s,'D13','graphite rods','electrodes/precursor',raw='99.99%;spacing6cm',loc='p2 §2.2')
    component(s,'D13','HCl electrolyte','electrolyte',500,'mL',raw='3mM HCl;500mL',loc='p2 §2.2')
    proc(s,'D13','CD_synthesis','electrochemical exfoliation30V;3mMHCl500mL;stir',time=24,source_locator='p2 §2.2')
    proc(s,'D13','purification','filter0.22um;8000rpm40min;dialysis300Da48h',time=48,source_locator='p2 §2.2')
    meas(s,'D13','surface_carboxyl_mmol_g',18.26,'mmol/g','p1 abstract',notes='用于苯酚Fenton协同降解；97.75%是苯酚去除率，不是杀菌率。')

    # Secondary reviews: topic/reference index, never training labels.
    for fid,loc,topic,note in [
        ('F23','p1 abstract; p18 §4.1.3','N-doping;surface charge;ROS;PTT','氮掺杂机制与前驱体索引。不要将N含量自动映射为抗菌强度；未逐条转录全部综述文献。'),
        ('F27','p1 abstract; p13-14 mechanisms','CDs in active food packaging','食品保存综合结果含阻隔/聚合物贡献，不能等同游离CD杀菌率。'),
        ('F32','p1 abstract','physical destruction;biochemical damage;synergy','机制综述，不新增独立配方；按原始DOI追索后去重。'),
        ('F33','p1 abstract','mechanism;design;applications','抗菌表面/生物膜/食品保存和成像属于不同测试对象。'),
        ('F34','p1 abstract; p16 conclusions','PDT versus PTT','光动力ROS与光热升温机制分开；记录波长/光强/时间/温度，而非仅写光照。'),
        ('F41','p1 abstract; p11 §3','MXene PTT background','二维MXene非CD；所有MXene杀菌数值均不进入碳点性能表。'),
    ]: review(fid,loc,'review topic index',topic,note)
    # C12 Table1 consists of heterogeneous aggregate ranges, not samples.
    for doping,prec,raw,refs in [
        ('metal','Fe,Zn,Cu,Co,Mn,Ag salts/metal-organic compounds','MIC1-32ug/mL','Tariq2023;Wang2024;Sara2024'),
        ('non-metal','glucosamine,malic acid,boric acid;N/N:S/N:P','MIC300-400ug/mL','Karaman2024'),
        ('co-doping','modified precursors with mixed dopants','MIC0.5-16ug/mL','Wu2024;Chen2025'),
        ('heavy metal','AgNO3;AuCl','MIC0.25-8ug/mL','Jiang2024'),
        ('rare earth','Gd,Ce;urea,citric acid','MIC16-32ug/mL','Wu2023'),
    ]:
        review('F43','p7 Table1; p8 comparability caveat',refs,f'{doping};{raw}',
               '跨研究汇总区间，菌株/协议/激发不同；不拆成精确MIC，不作金属优于非金属的定量排序，也不是PET实测。',precursor=prec,additive=doping)
    for loc,topic,statement in [
        ('p5-6','doping versus surface functionalization','掺杂改变电子结构；胺基质子化与表面配体控制净电荷；金属掺杂不必然使CD带正电。'),
        ('p8-10','membrane binding','zeta、粒径、表面基团、聚集、盐/蛋白环境和菌壁组成共同影响结合；阴性电位不等于无抗菌。'),
        ('p10-13','ROS/excitation','光谱匹配、缺陷、ROS种类与光强/时间/氧环境相关；ROS探针及清除剂实验不足以单独证明因果。'),
        ('p13-14','MurD hypothesis','MurD结合/竞争抑制需酶动力学或结构验证；本地原始Qie2022见D06/F36，不重复计研究。'),
        ('p14-16','DNA/protein/ATP','DNA断裂、转录组、ATP下降为不同证据层级；间接组学变化不等同直接靶点结合。'),
        ('p16-18','QS and EPS','群体感应、生物膜形成抑制、成熟膜清除、EPS破坏与浮游菌杀菌分开；QS抑制未必直接杀菌。'),
        ('p18-21','safety/stability','安全依赖剂量、表面电荷、金属释放及暴露时长；不能将普通细胞存活>80%视作所有配方安全。'),
        ('p19 Table2','theranostic platforms','金属CD、杂化平台、生物活性配体修饰平台为综述类别；需查原始研究，不作为独立样品。'),
    ]: review('F43',loc,'C12 mechanistic synthesis',topic,statement+' 当前仅机制/实验设计证据，include_primary_training=0。')
    for alg,ref,output in [
        ('RF/gradient boosting','Senanayake2022','emission wavelength/QY'),
        ('SVM/XGBoost','Hong2022','fluorescence/emission'),
        ('ANN/deep learning','Duman/Jalilov2024','optical spectrum,size,QY'),
        ('RF/XGBoost/CatBoost','Duman2026','photoluminescence'),
        ('ML+optimization','Mohammadzadeh2024','synthesis parameters'),
        ('QY prediction','Ren2026','QY'),
    ]: review('F43','p22 AI/ML; p23 Table4',ref,f'{alg};reported output:{output}',
               '综述列举的模型以光学/结构预测为主；未提供本任务抗菌外部验证集或通用精度。PLQY不能替代ROS量子产率或抗菌标签。')
    issue('C12','C12-review','causal_strength_and_fig2','正文p5-6说明金属掺杂不必然正电，Fig2标题却概括为正电；p23 Table4将高PLQY与ROS/抗菌关联，不能据此等同。','以正文限定和实际表征为准；分别记录PLQY/ROS/抗菌；综述只作假设来源。','F43','p5-6 Fig2; p22-23 Table4')
    issue('C12','C12-review','mixed_biological_evidence','p15基因机制段引用MCF7凋亡/G0G1例子，并非细菌抗菌实验；MurD竞争抑制在p13-14又明确证据不足。','不把哺乳动物细胞周期或综述机制推断填成细菌实验标签；机制结论区分直接/间接证据。','F43','p13-15')
    return routes,queue
