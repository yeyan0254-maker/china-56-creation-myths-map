#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# 中国 56 个民族创世神话地图 · 免费本地批量神经配音生成脚本（V3.4 升级版）
# 依赖安装：pip install edge-tts
# 运行方式：将本脚本放到与 HTML 同目录下，终端执行 python generate_audio_pack.py
# 生成结果：
#   1. 自动输出 56 条高质量普通话精配 MP3（./assets/audio/mandarin/{stem}.mp3）
#   2. 自动输出 12 族真实可用汉语方言与多语种神经语音 MP3（./assets/audio/native/{stem}.mp3）
#   3. 自动扫描 ./assets/ 下全部 .webp/.png/.mp3/.wav/.ogg/.m4a 并合并更新 ./assets/manifest.js（保留已有 .wav 器乐）
import asyncio, json, os
import edge_tts

MANDARIN_VOICE = "zh-CN-YunjianNeural"  # 沉稳国风说书人男声（可改为 zh-CN-XiaoxiaoNeural 女声）

# 12 族真实可用方言与多语种神经语音映射（外语条目配对应真实语种短句，绝不乱念中文）
NATIVE_VOICE_MAP = {
    "han":      ("zh-CN-henan-YundengNeural", None),
    "hui":      ("zh-CN-shaanxi-XiaoniNeural", None),
    "gaoshan":  ("zh-TW-YunJheNeural", None),
    "man":      ("zh-CN-liaoning-XiaobeiNeural", None),
    "yi":       ("zh-CN-sichuan-YunxiNeural", None),
    "qiang":    ("zh-CN-sichuan-YunxiNeural", None),
    "tujia":    ("zh-CN-sichuan-YunxiNeural", None),
    "zhuang":   ("zh-HK-HiuGaaiNeural", "壮族创世史诗《布洛陀》：布洛陀开辟天地，定立三界，开创壮乡文明。"),
    "chaoxian": ("ko-KR-SunHiNeural", "단군 신화. 태백산 신단수 아래에서 웅녀와 환웅이 만나 단군을 낳았습니다."),
    "russian":  ("ru-RU-SvetlanaNeural", "Древняя легенда о солнце Ярило и весеннем обновлении земли."),
    "mongol":   ("mn-MN-YesuiNeural", "Бөртэ Чоно, Гоо Марал. Монголчуудын эртний домог."),
    "kazakh":   ("kk-KZ-AigulNeural", "Жасаған дүниені жаратты. Қазақ халқының көне аңызы."),
    "uzbek":    ("uz-UZ-MadinaNeural", "Alpomish dostoni va qadimgi Ipak yoʻli merosi."),
    "jing":     ("vi-VN-HoaiMyNeural", "Lạc Long Quân và Âu Cơ sinh trăm trứng, khởi nguồn non sông biển cả."),
}

MYTHS = [
  {
    "stem": "han",
    "ethnic": "汉族",
    "province": "河南",
    "nativeLabel": "中原方言",
    "text": "汉族创世神话《盘古开天与女娲造人》讲述：远古宇宙混沌如卵，盘古挥斧劈开天地，身躯化作日月山川；此后女娲抟土造人，开启华夏人间烟火。"
  },
  {
    "stem": "zhuang",
    "ethnic": "壮族",
    "province": "广西",
    "nativeLabel": "壮语",
    "text": "壮族创世史诗《布洛陀》唱道：远古始祖布洛陀与姆六甲劈分混沌、定立三界，以泥土造出人类，又取来火种与稻谷，开创了壮乡农耕文明。"
  },
  {
    "stem": "man",
    "ethnic": "满族",
    "province": "吉林",
    "nativeLabel": "满语",
    "text": "满族萨满创世神话讲述：创世女神阿布卡赫赫在混沌中苏醒，吹气化出日月星辰，采撷神圣柳叶造出人类，护佑长白山与黑水大地。"
  },
  {
    "stem": "hui",
    "ethnic": "回族",
    "province": "宁夏",
    "nativeLabel": "西北方言",
    "text": "回族传统口述融合了天地造化、泥土造人的宇宙观，以及唐宋元时期先民循丝绸之路东来、扎根黄河两岸与各族交融共生的族源记忆。"
  },
  {
    "stem": "miao",
    "ethnic": "苗族",
    "province": "贵州",
    "nativeLabel": "苗语",
    "text": "苗族古歌唱道：古老枫木树心化出蝴蝶妈妈，产下十二枚神蛋，经鹡宇鸟精心孵化，从中诞生了苗族始祖姜央与世间万物生灵。"
  },
  {
    "stem": "uyghur",
    "ethnic": "维吾尔族",
    "province": "新疆",
    "nativeLabel": "维吾尔语",
    "text": "古籍史诗《乌古斯传》讲述：英雄乌古斯可汗迎娶天光与圣树仙女，育有日月星辰与天地山海六子，在神异苍狼的指引下开辟家园。"
  },
  {
    "stem": "tujia",
    "ethnic": "土家族",
    "province": "湖南",
    "nativeLabel": "土家语",
    "text": "土家族《摆手歌》唱道：张古老织天，李古老造地，为让天地相合，把大地挤出了武陵群山与溪谷；洪水之后，葫芦里的兄妹重续人类。"
  },
  {
    "stem": "yi",
    "ethnic": "彝族",
    "province": "四川",
    "nativeLabel": "彝语",
    "text": "彝族创世史诗《勒俄特依》讲述：神雪降世孕育出万物与人类，面对六个太阳炙烤大地，英雄支格阿鲁弯弓射落多余日月，护佑苍生。"
  },
  {
    "stem": "mongol",
    "ethnic": "蒙古族",
    "province": "内蒙古",
    "nativeLabel": "蒙古语",
    "text": "《蒙古秘史》开篇记载：承受天命降生的苍狼与灵秀白鹿渡过浩瀚水泽，在斡难河源头的圣山下定居繁衍，成为草原先民的古老始祖。"
  },
  {
    "stem": "zang",
    "ethnic": "藏族",
    "province": "西藏",
    "nativeLabel": "藏语",
    "text": "《西藏王统记》记载：慈悲神猴在雪域雅砻山洞与岩罗刹女结为伴侣，后代采食神赐青稞与五谷后褪去尾毛，演化为最早的藏族先民。"
  },
  {
    "stem": "buyi",
    "ethnic": "布依族",
    "province": "贵州",
    "nativeLabel": "布依语",
    "text": "布依族创世古歌唱道：盘果王劈分天地万物，勇士力嘎兜射落十一个多余太阳，后经洪水劫难，躲在大葫芦里的兄妹重续人间血脉。"
  },
  {
    "stem": "dong",
    "ethnic": "侗族",
    "province": "贵州",
    "nativeLabel": "侗语",
    "text": "侗族大歌传唱：远古祖母神护佑天地，巨龟孵出四枚神蛋诞生人祖；洪水滔天时，姜良姜妹躲进大葫芦幸存，重兴侗乡人类文明。"
  },
  {
    "stem": "yao",
    "ethnic": "瑶族",
    "province": "广西",
    "nativeLabel": "瑶语",
    "text": "瑶族创世史诗《密洛陀》唱道：创世女神密洛陀开辟天地，巧用蜂蜡与沃土捏出人形并吹入灵气，化作最早的瑶族先民。"
  },
  {
    "stem": "chaoxian",
    "ethnic": "朝鲜族",
    "province": "吉林",
    "nativeLabel": "朝鲜语",
    "text": "朝鲜族经典神话讲述：天神之子桓雄降临太白山神檀树下，母熊潜心守戒、食艾化作熊女，与桓雄结合诞下了人文始祖檀君。"
  },
  {
    "stem": "bai",
    "ethnic": "白族",
    "province": "云南",
    "nativeLabel": "白语",
    "text": "白族口传古歌讲述：远古盘古盘生开辟苍山洱海，后来洪水淹没大地，一对善良兄妹躲进大葫芦渡过劫难，在点苍山下重续人烟。"
  },
  {
    "stem": "hani",
    "ethnic": "哈尼族",
    "province": "云南",
    "nativeLabel": "哈尼语",
    "text": "哈尼族创世史诗《奥色密色》吟唱：云雾凝结出创世母神塔婆，巨鱼身躯化作绵延大地与江河，指引先民修筑出层叠壮美的梯田家园。"
  },
  {
    "stem": "kazakh",
    "ethnic": "哈萨克族",
    "province": "新疆",
    "nativeLabel": "哈萨克语",
    "text": "哈萨克族创世神话《迦萨甘创世》传唱：造物神迦萨甘织就璀璨星空，命巨角青牛托举大地，圣洁白天鹅化育生灵，开创了伊犁与阿勒泰草原文明。"
  },
  {
    "stem": "li",
    "ethnic": "黎族",
    "province": "海南",
    "nativeLabel": "黎语",
    "text": "黎族创世神话讲述：远古大力神劈分南海云雾铸成五指山，雷公在黎母山遗落神蛋孵出女神黎母，孕育了绵延琼州的黎族先民。"
  },
  {
    "stem": "dai",
    "ethnic": "傣族",
    "province": "云南",
    "nativeLabel": "傣语",
    "text": "傣族贝叶经创世史诗《巴塔麻嘎捧尚罗》记载：创世大神英叭自风雾中诞生，搓揉香泥抛入水面化作沃土大地，并塑出人类与孔雀万物。"
  },
  {
    "stem": "she",
    "ethnic": "畲族",
    "province": "福建",
    "nativeLabel": "畲语",
    "text": "畲族史诗《高皇歌》传唱：神异龙麒盘瓠立功迎娶三公主，辞别宫廷移居凤凰山与东南群峰，开启了盘、蓝、雷、钟四姓繁衍的山哈文明。"
  },
  {
    "stem": "lisu",
    "ethnic": "傈僳族",
    "province": "云南",
    "nativeLabel": "傈僳语",
    "text": "傈僳族《创世纪》古歌吟唱：天神木布帕劈分天地、筑起高山峡谷；大洪水袭来时，善良兄妹躲进大葫芦渡过劫难，在怒江两岸重续人间烟火。"
  },
  {
    "stem": "gelao",
    "ethnic": "仡佬族",
    "province": "贵州",
    "nativeLabel": "仡佬语",
    "text": "仡佬族古老传说讲述：大力神亚歪立柱撑开天地，江面漂来的一节灵异巨竹破节生出英勇竹王，成为黔北先民世代敬仰的生命图腾。"
  },
  {
    "stem": "dongxiang",
    "ethnic": "东乡族",
    "province": "甘肃",
    "nativeLabel": "东乡语",
    "text": "东乡族口传族源讲述：先民循古丝路扎根甘肃临夏黄土山塬，寻得甘冽神泉开垦良田，在洮河与大夏河畔谱写出勤劳坚韧的家园故事。"
  },
  {
    "stem": "gaoshan",
    "ethnic": "高山族",
    "province": "台湾",
    "nativeLabel": "高山族语",
    "text": "台湾高山族口传神话讲述：远古天空挂着两个太阳，勇士背着幼子远征，两代人接力射伤其中一轮太阳化为明月，从此宝岛有了昼夜更替与漫天星辰。"
  },
  {
    "stem": "lahu",
    "ethnic": "拉祜族",
    "province": "云南",
    "nativeLabel": "拉祜语",
    "text": "拉祜族创世史诗《牡帕密帕》记载：天神厄莎搓泥造天地，请蜘蛛织稳天穹，又种下神异大葫芦。老鼠咬开葫芦壳后，走出了人类始祖扎笛与娜笛。"
  },
  {
    "stem": "shui",
    "ethnic": "水族",
    "province": "贵州",
    "nativeLabel": "水语",
    "text": "水族古歌《开天辟地歌》唱道：创世女神牙巫劈开混沌、造出天地星辰，经历射日与洪水劫难后，先民在都柳江畔开创了古老水书文明。"
  },
  {
    "stem": "wa",
    "ethnic": "佤族",
    "province": "云南",
    "nativeLabel": "佤语",
    "text": "佤族史诗《司岗里》传唱：大神梅依吉开辟阿佤山后，小米雀啄开圣洞司岗，佤族与汉、拉祜、傣等各族先祖携手走出，共建美丽家园。"
  },
  {
    "stem": "naxi",
    "ethnic": "纳西族",
    "province": "云南",
    "nativeLabel": "纳西语",
    "text": "纳西族东巴经《崇搬图》讲述：远古洪水淹没大地，善良的崇仁利恩躲进牦牛皮鼓幸存下来，后来迎娶天女衬红褒白，在雪山下重续人间烟火。"
  },
  {
    "stem": "qiang",
    "ethnic": "羌族",
    "province": "四川",
    "nativeLabel": "羌语",
    "text": "羌族史诗《木姐珠与斗安珠》讲述：天女木姐珠倾慕牧羊青年斗安珠，携天界五谷与火种降临岷江高山，在圣洁白石护佑下开启云端羌寨文明。"
  },
  {
    "stem": "tu",
    "ethnic": "土族",
    "province": "青海",
    "nativeLabel": "土族语",
    "text": "土族古歌《天地开辟》唱道：远古神祇拨开黑雾、铸就日月山川，彩霞织就土家七彩霓裳，先民跨越雪岭在青海河湟谷地建起彩虹故乡。"
  },
  {
    "stem": "mulao",
    "ethnic": "仫佬族",
    "province": "广西",
    "nativeLabel": "仫佬语",
    "text": "仫佬族《古条歌》讲述：勇士布伯智擒雷公，大洪水降临时，善良兄妹躲进神牙长出的巨大葫芦渡过劫难，在罗城群山间重续人烟。"
  },
  {
    "stem": "xibe",
    "ethnic": "锡伯族",
    "province": "新疆",
    "nativeLabel": "锡伯语",
    "text": "锡伯族口传记忆融合了东北古老源流与守护子孙的喜利妈妈信仰，以及清代先民万里西迁伊犁河谷、开渠兴农的壮丽史诗。"
  },
  {
    "stem": "kirgiz",
    "ethnic": "柯尔克孜族",
    "province": "新疆",
    "nativeLabel": "柯尔克孜语",
    "text": "柯尔克孜族古老族源传说讲述：四十位纯洁姑娘饮下帕米尔圣泉的奇异白沫，孕育出四十个勇敢部落，在雪山草原间传唱千年英雄史诗。"
  },
  {
    "stem": "daur",
    "ethnic": "达斡尔族",
    "province": "内蒙古",
    "nativeLabel": "达斡尔语",
    "text": "达斡尔族萨满创世神话讲述：远古世界一片汪洋，神鸟潜入海底衔回泥沙化作嫩江黑土大地，雄鹰世代翱翔守护达斡尔先民。"
  },
  {
    "stem": "jingpo",
    "ethnic": "景颇族",
    "province": "云南",
    "nativeLabel": "景颇语",
    "text": "景颇族创世史诗《木脑斋瓦》吟唱：创世英雄宁贯娃锻实大地、开凿江河；滔天洪水之后，藏身大木鼓里的兄妹重续人类，跳起欢腾的目瑙纵歌。"
  },
  {
    "stem": "maonan",
    "ethnic": "毛南族",
    "province": "广西",
    "nativeLabel": "毛南语",
    "text": "毛南族排歌唱道：盘古辟开天地铸就桂北奇峰，漫天洪水来袭时，善良兄妹藏身大葫芦安然渡劫，在环江群山间重续人间烟火。"
  },
  {
    "stem": "sala",
    "ethnic": "撒拉族",
    "province": "青海",
    "nativeLabel": "撒拉语",
    "text": "撒拉族族源史诗《骆驼泉》讲述：先祖尕勒莽兄弟牵着白骆驼万里东迁，抵达青海循化时白驼化为白石、涌出甘泉，成为撒拉族世代定居的美好家园。"
  },
  {
    "stem": "blang",
    "ethnic": "布朗族",
    "province": "云南",
    "nativeLabel": "布朗语",
    "text": "布朗族创世神话《顾米亚》唱道：巨人顾米亚以巨犀身躯化作天地山川与江河，又率子射落多余烈日，将千年茶种留给了布朗山先民。"
  },
  {
    "stem": "tajik",
    "ethnic": "塔吉克族",
    "province": "新疆",
    "nativeLabel": "塔吉克语",
    "text": "《大唐西域记》记载了帕米尔高原汉日天种的瑰丽传说：东方公主在雪山孤峰感太阳神光诞下先祖，帕米尔雄鹰世代护佑着塔吉克儿女。"
  },
  {
    "stem": "achang",
    "ethnic": "阿昌族",
    "province": "云南",
    "nativeLabel": "阿昌语",
    "text": "阿昌族创世史诗《遮帕麻和遮米麻》唱道：天公遮帕麻造天，地母遮米麻织地，两人合力射落恶魔铸造的假太阳，又撒下葫芦籽孕育出人类先民。"
  },
  {
    "stem": "pumi",
    "ethnic": "普米族",
    "province": "云南",
    "nativeLabel": "普米语",
    "text": "普米族古歌《洪水滔天》吟唱：远古大水淹没群山，善良先祖藏身牛皮囊幸存下来，迎娶天女重续人间，带领族人跨越雪山定居横断山脉。"
  },
  {
    "stem": "ewenki",
    "ethnic": "鄂温克族",
    "province": "内蒙古",
    "nativeLabel": "鄂温克语",
    "text": "鄂温克族神话讲述：天神恩都力采撷大兴安岭黑土与山泉灵气造出人类，林海先民尊奉神熊为先祖，与驯鹿相伴守护苍茫白桦林。"
  },
  {
    "stem": "nu",
    "ethnic": "怒族",
    "province": "云南",
    "nativeLabel": "怒语",
    "text": "怒族创世古歌讲述：女始祖与勤劳蜂王、神蛇结缘孕育古老氏族，经历滔天洪水之后，幸存兄妹在碧罗雪山与怒江峡谷重续人间烟火。"
  },
  {
    "stem": "jing",
    "ethnic": "京族",
    "province": "广西",
    "nativeLabel": "京语",
    "text": "京族《哈歌》传说讲述：海龙之后貉龙君与山仙妪姬结为连理，一胞百卵孵出百名儿郎，五十入山、五十赴海，开启了京族三岛独弦琴声伴浪花的海洋文明。"
  },
  {
    "stem": "jino",
    "ethnic": "基诺族",
    "province": "云南",
    "nativeLabel": "基诺语",
    "text": "基诺族创世史诗《阿嫫腰北》唱道：创世女神阿嫫腰北开辟基诺山茶林，洪水来袭时造出大鼓护送兄妹玛黑与玛妞幸存，留传下雄浑的太阳大鼓舞。"
  },
  {
    "stem": "deang",
    "ethnic": "德昂族",
    "province": "云南",
    "nativeLabel": "德昂语",
    "text": "德昂族创世史诗《达古达楞格莱标》传唱：神山之巅的古老茶树被神风吹落一百零二片茶叶，化作五十一对男女，成为古老茶农德昂族的先祖。"
  },
  {
    "stem": "baoan",
    "ethnic": "保安族",
    "province": "甘肃",
    "nativeLabel": "保安语",
    "text": "保安族口传族源讲述：先民自青海保安城跋涉迁徙至甘肃积石山下，引水垦田、淬火百炼锻造出精湛的保安腰刀，谱写了多民族融合的家园史话。"
  },
  {
    "stem": "russian",
    "ethnic": "俄罗斯族",
    "province": "新疆",
    "nativeLabel": "俄语/北疆方言",
    "text": "中国俄罗斯族传承了礼赞太阳与彩蛋新生的古老民俗，先民在新疆伊犁塔城与额尔古纳河畔筑起温暖的木刻楞木屋，谱写出北疆多元共融的乐章。"
  },
  {
    "stem": "yugur",
    "ethnic": "裕固族",
    "province": "甘肃",
    "nativeLabel": "裕固语",
    "text": "裕固族叙事古歌《西至哈至》深情追忆黄头回鹘先民翻越戈壁、扎根祁连山草原的壮阔历程，并与天鹅仙女传说共同织就河西牧歌。"
  },
  {
    "stem": "uzbek",
    "ethnic": "乌孜别克族",
    "province": "新疆",
    "nativeLabel": "乌孜别克语",
    "text": "乌孜别克族口传族源融汇了中亚绿洲文明与古老草原诗韵，先民沿丝绸之路翻越葱岭定居天山南北，以精巧织锦与手鼓乐舞点亮丝路繁华。"
  },
  {
    "stem": "menba",
    "ethnic": "门巴族",
    "province": "西藏",
    "nativeLabel": "门巴语",
    "text": "门巴族口传古歌讲述：远古神猴化生雪域人类，后世先民跨越喜马拉雅雪峰寻访莲花秘境，在勒布沟与墨脱密林间架起藤桥、筑就家园。"
  },
  {
    "stem": "orqen",
    "ethnic": "鄂伦春族",
    "province": "黑龙江",
    "nativeLabel": "鄂伦春语",
    "text": "鄂伦春族古老神话传唱：天神恩都力命神鸟衔泥造出兴安岭大地并塑出人类，面对烈日炙烤山林，勇敢猎人弯弓射落多余太阳，护佑北国林海。"
  },
  {
    "stem": "dulong",
    "ethnic": "独龙族",
    "province": "云南",
    "nativeLabel": "独龙语",
    "text": "独龙族创世古歌吟唱：天神噶美与噶萨开辟独龙江峡谷，英雄拉弓射落多余的八个太阳，洪水之后幸存兄妹重续人类，织就绚丽的独龙彩毯。"
  },
  {
    "stem": "tatar",
    "ethnic": "塔塔尔族",
    "province": "新疆",
    "nativeLabel": "塔塔尔语",
    "text": "中国塔塔尔族口传记忆承载着先民远行定居新疆天山北麓的历程，每逢春耕后的萨班节，族人以欢快的手风琴歌舞礼赞大地的丰收与生机。"
  },
  {
    "stem": "hezhe",
    "ethnic": "赫哲族",
    "province": "黑龙江",
    "nativeLabel": "赫哲语",
    "text": "赫哲族伊玛堪史诗传唱：古时天上有三个太阳烤干了三江鱼场。英雄莫日根攀上最高雪峰，弯弓连射两箭落双日，为大地换回清凉与四季更迭。"
  },
  {
    "stem": "luoba",
    "ethnic": "珞巴族",
    "province": "西藏",
    "nativeLabel": "珞巴语",
    "text": "珞巴族创世史诗《阿巴达尼》吟唱：天地孕育光明万物，智慧始祖阿巴达尼射落多余烈日、取回人间火种，引领珞巴先民在喜马拉雅密林繁衍生息。"
  }
]

async def synth(text, voice, out_path):
    if os.path.exists(out_path) and os.path.getsize(out_path) > 1000:
        return True
    try:
        comm = edge_tts.Communicate(text, voice, rate="-4%")
        await comm.save(out_path)
        return True
    except Exception as exc:
        print(f"   [跳过] {out_path} 合成失败（可稍后重试）：{exc}")
        return False

def scan_media(folder, exts):
    if not os.path.isdir(folder):
        return []
    return sorted([f for f in os.listdir(folder) if f.lower().endswith(exts)])

async def main():
    os.makedirs("assets/stickers", exist_ok=True)
    os.makedirs("assets/audio/mandarin", exist_ok=True)
    os.makedirs("assets/audio/native", exist_ok=True)
    for idx, item in enumerate(MYTHS, 1):
        stem = item["stem"]
        m_path = f"assets/audio/mandarin/{stem}.mp3"
        print(f"[{idx:02d}/56] 合成普通话：{item['ethnic']} -> {m_path}")
        await synth(item["text"], MANDARIN_VOICE, m_path)
        if stem in NATIVE_VOICE_MAP:
            n_voice, custom_txt = NATIVE_VOICE_MAP[stem]
            n_path = f"assets/audio/native/{stem}.mp3"
            print(f"       同步合成原声/方言：{item['nativeLabel']} ({n_voice}) -> {n_path}")
            await synth(custom_txt or item["text"], n_voice, n_path)
    stickers_done = scan_media("assets/stickers", (".webp", ".png", ".jpg", ".jpeg"))
    mandarin_done = scan_media("assets/audio/mandarin", (".mp3", ".wav", ".ogg", ".m4a"))
    native_done = scan_media("assets/audio/native", (".mp3", ".wav", ".ogg", ".m4a"))
    manifest_js = (
        "// 自动生成的全格式离线素材清单（V3.4 兼容 .wav 器乐与 .mp3 原声共存）\n"
        "window.MYTH_ASSETS = {\n"
        f"  stickers: {json.dumps(stickers_done, ensure_ascii=False)},\n"
        f"  mandarinAudio: {json.dumps(mandarin_done, ensure_ascii=False)},\n"
        f"  nativeAudio: {json.dumps(native_done, ensure_ascii=False)}\n"
        "};\n"
    )
    with open("assets/manifest.js", "w", encoding="utf-8") as mf:
        mf.write(manifest_js)
    print(f"\n完成！清单已更新：贴纸 {len(stickers_done)} 项，普通话 {len(mandarin_done)} 项，民族原声/器乐 {len(native_done)} 项。")

if __name__ == "__main__":
    asyncio.run(main())
