#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Created by Pengying Wang on 2019-09-28
import requests
import networkx as nx
import datetime
import collections
import random
import community
import matplotlib.pyplot as plt
import collections
import json


daily_query_api_prefix = "https://api.pushshift.io/reddit/submission/search/?subreddit=hongkong&"
comments_query_api_prefix = "https://api.pushshift.io/reddit/comment/search/?link_id="
author_query_api_prefix = "https://api.pushshift.io/reddit/search/comment/?author="


def query_api(date, interval, limit, trust_list):
    first_next_day = (datetime.datetime.strptime(date, "%Y-%m-%d") + datetime.timedelta(days=15)).strftime('%Y-%m-%d')
    request = daily_query_api_prefix + "after=" + date + "&before=" + first_next_day + "&limit=" + str(limit)
    # Get all the topics published in subreddit - hongkong in one day (date). in Json format
    json_data = requests.get(request).json()['data']
    graph = nx.Graph()
    weight_dic = collections.defaultdict(int)
    id_user_dic = {}
    for data in json_data:
        user = data['author']
        graph.add_node(user)
        # link id for topic
        raw_id = data['id']
        if raw_id not in id_user_dic and user != "[deleted]":
            id_user_dic[raw_id] = user

        num_comments = data['num_comments']
        if num_comments != 0:
            graph, weight_dic = build_edge(raw_id, graph, id_user_dic, weight_dic)
    for ele in trust_list:
        graph.remove_node(ele)
        if ele in weight_dic:
            del weight_dic[ele]
    second_day = (datetime.datetime.strptime(first_next_day , "%Y-%m-%d") + datetime.timedelta(days=15)).strftime('%Y-%m-%d')
    second_request = daily_query_api_prefix + "after=" + first_next_day + "&before=" + second_day + "&limit=" + str(limit)
    second_json_data = requests.get(second_request).json()['data']

    for data in second_json_data:
        user = data['author']
        graph.add_node(user)
        # link id for topic
        raw_id = data['id']
        if raw_id not in id_user_dic and user != "[deleted]":
            id_user_dic[raw_id] = user

        num_comments = data['num_comments']
        if num_comments != 0:
            graph, weight_dic = build_edge(raw_id, graph, id_user_dic, weight_dic)
    print("edges"+str(graph.edges))
    return graph, weight_dic, id_user_dic


def build_edge(link_id, graph, id_user_dic, weight_dic):
    parent_dic = {}
    request = comments_query_api_prefix + link_id
    try:
        json_data = requests.get(request).json()['data']
        for data in json_data:
            child_id = data['id']
            author = data['author']
            graph.add_node(author)
            if child_id not in id_user_dic and author != "[deleted]":
                id_user_dic[child_id] = author
            parent_id = data['parent_id']
            if '_' in parent_id:
                parent_id = parent_id.split("_")[1]
            if parent_id not in parent_dic:
                parent_dic[parent_id] = set()
            parent_dic[parent_id].add(child_id)
        for key, children in parent_dic.items():
            # random shuffle children
            children = list(children)
            # random.shuffle(children)
            # cut = random.randint(0, len(children))
            # child_1 = children[:cut]
            # child_2 = children[cut:]
            # # print("children1 " + str(len(child_1)))
            # # print("children2 " + str(len(child_2)))
            # connect(child_1, graph, id_user_dic, weight_dic)
            # connect(child_2, graph, id_user_dic, weight_dic)
            graph, weight_dic = connect(children, graph, id_user_dic, weight_dic)
        return graph, weight_dic
    except json.decoder.JSONDecodeError:
        pass


def connect(children, graph, id_user_dic, weight_dic):
    if len(children) <= 1:
        return
    for i in children:
        for j in children:
            if i != j:
                if i in id_user_dic and j in id_user_dic:
                    user_i = id_user_dic[i]
                    user_j = id_user_dic[j]
                    if (user_i, user_j) in weight_dic:
                        weight_dic[(user_i, user_j)] += 1
                    else:
                        weight_dic[(user_i, user_j)] = 1
    return graph, weight_dic


def counter_attack(dict, fake):
    random.shuffle(fake)
    if len(fake) >= 20:
        for i in range(0, len(fake)-1, 20):
            new_connect(fake[i:i+1], dict)
    return dict


def new_connect(lst, w_dict):
    for i in lst:
        for j in lst:
            if i != j:
                w_dict[(i, j)] = w_dict.get((i, j), 0) + 1
    return w_dict


def get_uncomment(graph, w_dict, trust_list):
    for ele in trust_list:
        graph.remove_node(ele)
        del w_dict[ele]
    return graph, w_dict


def plot_community(G, partition):
    size = float(len(set(partition.values())))
    pos = nx.spring_layout(G)
    count = 0.
    for com in set(partition.values()):
        count += 1
    list_nodes = [nodes for nodes in partition.keys()
                  if partition[nodes] == com]
    nx.draw_networkx_nodes(G, pos, list_nodes, node_size=20,
                           node_color=str(count / size))
    nx.draw_networkx_edges(G, pos, alpha=0.5)
    plt.show()


def count_community(part):
    count = collections.defaultdict(list)
    for key, value in part.items():
        count[value].append(key)
    num_count = {}
    for key, value in count.items():
        num_count[key] = len(value)
    # num_count.sort(num_count.items(), key=lambda x:x[1])
    dic_lst = sorted(num_count.items(), key=lambda x:(-x[1]))
    return dic_lst


def attack(w_dict, fake_list):
    for i in fake_list:
        for j in fake_list:
            if i != j:
                w_dict[(i, j)] = w_dict.get((i, j), 0) + 1
    # for i in two_list:
    #     for j in two_list:
    #         if i != j:
    #             w_dict[(i, j)] = w_dict.get((i, j), 0) + 1
    return w_dict



if __name__ == '__main__':
    new_set = {'MyAccountRuns', 'idonthaveacoolname13', 'angrytwerker', 'Future441', 'bosfton', 'The-Last-Summer', 'aajin', 'buffopmartianboi', 'hundrafemtio', 'Luke_LMV', 'ServedNoodles', 'tottenhamlimbs', 'strikefreedompilot', 'kafkaonshore', 'Herkentyu_cico', 'clang823', 'FaustiusTFattyCat613', 'GabhaNua', 'Yuanlairuci', 'kaycee1992', 'firen777', 'Chuchumaruu', 'Doubtitcopper', 'schnappi2', 'Nudetypist', 'SciFiJesseWardDnD', 'Yurion13', 'NewYorkais', 'defaultskin2', 'canto-ling', 'rosesarebIack', 'Tarfire42', 'Doctor-TJEckleburg', 'rackcountry', 'Breshawnashay', 'imbantam', 'robostrike', 'Buuksta', 'ummusername', 'PandaOfBunnies', 'late2party', 'Stalslagga', 'BigBulkemails', 'Cunt_squared', 'stormbreaker4urheart', 'thephenom', 'Wildicki', 'LilithScout', 'Omega9800', 'XDivider', 'Mister-Kool-Aid', 'zeta7124', 'mickaelbneron', 'Jedi_Revan', 'DefinitionOfFear', 'kuolinn', 'DutchMeteor', 'KungFusedMike', 'renmenbibi', 'Progenitor001', 'tangerinejoy228', 'rocharox', 'ff_525', 'BasedAssadReturns', 'TravelPhoenix', 'ihatefilialpiety', 'Kitsunemitsu', 'Overcast30', 'Corner_Post', 'mishka0111', 'ALotOfRice', 'jacquesperry', 'la_mwnmwn', 'testedonsheep', 'LanEvo7685', 'Rilanara', 'gtsomething', 'GlobTrotters', 'EverybodyGetsCheese', 'lejfanbejfans_farmor', 'j_blackshadow', 'chugotleung2016', 'jayklk', 'GalantnostS', 'HammerSpam', 'joker_wcy', 'pigsonthewingz', 'flyingrobotpig', 'tobyclh', 'Danger_Dwarf17', 'RepF1A', 'Han-Do-Jin', 'Tungsten_Rain', 'Whimsycottt', 'swatgreat', 'UnoKitty', 'I_RIDE_SHORTSKOOLBUS', 'jynxbaba87', 'sesameseed88', 'Brave_Sir_Robin__', '-Thnift-', 'NinjahBob', 'Iblis824', 'Tickle-Bones', 'terry_banks', 'burningbun', 'bricknermonfan', 'fennej', 'potatopunchies', 'uberduck', '6nicemaymay9', 'jay1sb', 'toxicpast', 'stroopkoeken', 'monkeypie1234', 'gucci-legend', 'germainelol', 'Eitoku_K', 'ImpulseSnail2', 'polandCANintospace20', 'truehker', 'blue2usk', 'shilabula', 'wuliwala', '[deleted]', 'GeekyDoesReddit', 'SGarnier', 'DoctorKrusher', 'sexweedncigs', 'ogstepdad', 'Testing123xyz', 'chairmanwumao', 'sadboisadgurl', 'The_Thurmanator', 'endkkkterror', 'bubbybyrd', 'mma21x', 'TheTigerOfHK', 'Webcrack12', '2035WillBeGreat', 'JackHazardous', '_Manfred_', 'POCKETB00K1337', 'Shark_Fucker', 'ThatOneKid235', 'djrocks420', 'truer_DNA', 'petitecannon', 'dainthomas', 'wot0', 'HeungMinSonaldo7', '350Points', 'halftosser', 'Lauer99', 'Gabelolguy', 'EridanusVoid', 'TylerTheWolf123', 'Century64', 'Chemical_Violinist', 'Link-Amp', 'tinyrickross', 'mcTw2wZNvAmjvRMour2h', 'Zombiellen', 'doommagic1', 'hKthrowaway_789', 'dragon_sush1', 'Engine365', 'vikingbiochemist', 'needcleverpseudonym', 'No1BTSstanAccount', 'depo1983', 'torbn', 'mikedpoole', 'd0pedog', 'knigja', 'SpectrixYT', 'avid_procrastinator_', 'droptester', 'chromiselda', 'battleship217', 'biggiejon', 'mrjayviper', 'glycerethe', 'Silverwhitemango', 'SuperGrandor', 'BOXDisme', 'HereUThrowThisAway', 'xKnightly', 'nighthawk2019', 'neinMC', 'Nebben86', 'blackbloc1', 'somethingmichael', 'dreamerwakeup', 'DigitalMystik', 'GrandDukeofLuzon', 'euphraties247', 'FenceThinkHear', 'breezeaway1', 'Twitch_Tsunami_X', 'nakedpaddington', 'thematchalatte', 'WhineyVegetable', 'cuteshooter', 'Suremantank', 'chiefpat450119', 'passarinhodeak', 'danhoyuen', 'Megneous', 'Zman201', 'Localmotivator', 'EverythingIsNorminal', 'squareheadhk', 'gwairide', 'kennychwk', 'koolman7', 'itzvincentx3', 'Kuecke', 'holangjai', 'KyleEvans', 'JABHK', 'dynobot7', 'honsworth', 'debito128', '28th_boi', 'surprisesugarfree', 'toma17171', 'bicboi235', 'cti112', 'kJ2Y19HOStlBpKGSlBDK', 'emmytee', 'Nomie-Now', 'KRIEEEG', 'ymcatar0', 'HeartStarJester', 'lisabbqgirl', 'Saw_Good_Man', 'newrabbid', 'ibopm', 'tromboneface', 'NoisyFerox', 'Sapr_', 'SodaSplash', 'ronin_JR', 'KyoueiShinkirou', 'Lost_Tourist_61', 'Minoltah', 'caantoun', 'kimlorio', 'HKAzxc', 'stayhomedaddy', 'WeeklyIntroduction42', 'nikefan03', 'kaqing8', 'gabolicious', 'SCP-1', 'wdiva12121999', 'selphiefairy', 'GoRush87', 'Chocobean', 'JampoSpeaksForMoney', 'NachzehrerL', 'Steam_W0rks', 'houstonianisms', 'Giimax', 'joealmighty01', 'TuckerMcInnes', 'godrayden', 'pygocaribe', 'TheIlluminatedone13', 'HKVOAAP', 'flowbrother', 'poopfeast180', 'NiMiXeS', 'Annamman', 'looplox', 'KnowingRecipient', 'wha2les', 'oursondechine', 'SpecialistPlatypus', 'jackychanwo', 'NotASuicidalRobot', '-ipa', 'notmycharmander', 'lidge7012', 'fitterjohn', 'ConstantInteraction', 'Larry17', 'JoshTheRussian', 'TimelyPhoton', 'ItsAllOurBlood', 'c0p', 'tomazws', 'crispymoonshine', 'rentonwong', 'dennis_w', '-_asmodeus_-', 'J_Hutch64', 'Turd111', 'Little_Lightbulb', 'goldfish_memories', 'Moskau50', 'LogicalyetUnpopular', 'CaptainTeem000', 'Radge24', 'Ihavenofork', 'KaneCreole', 'Cyleni', 'ZePinkBaron', 'CookingLearner', 'ClickableLinkBot', 'josnowball', 'root_0f_all_cause', 'TheyGonHate', 'NikplaysgamesYT', 'alkalinecactus', 'Eat_the_Path', 'alvincf105', 'sensenjan', 'Xelium23', 'michael14375', 'Mad_Doggy_Dog', 'kingpug_asian', 'YenTheMerchant', 'Grifte6888', 'MxFragz', 'judoka320', 'ShoutingMatch', 'weddle_seal', 'Valo-FfM', 'Marrokiu20', 'apotheosis77', 'blackfyre69', 'bleepitybloop555', 'porkmantou', 'From_same_article', 'patm28', 'DrugHamster', 'E-X-Animus', 'highmejaime', 'YoYoThisIsJason', 'yaronSoo', 'NPC5175', 'AgnesTheAtheist', 'Deadeye_Spider', '_Forgot_name_', '-frozenfox-', 'Berzerka', 'tiangong', 'NextYin', 'groovytoon', '_xXpewdiepieShrekXx_', 'IloveSonicsLegs', 'brooklynnet32', 'WolzardFire', '1-1-2-1-RED-BLACK-GO', 'scrugbyhk', 'Toiisha', 'sonastyinc', 'JustALinuxNerd', 'competativevaper', 'HongKongPig', 'PandaPool69', 'HiThisisCarson', 'bearmc27', 'sarahlovesghost', 'Wardjinni', 'beepbeepwow', 'DerPoto', 'schmiggle_horn2020', 'SSiui', 'sgraBer1', 'starsmoonsun67', 'Megafro', 'hungzai', 'BluaBaleno', 'whocaresaboutnaming', 'VietCong0910', 'MT_SLAETTARATINDUR', 'boonus_boi', 'do_you_still_exist', 'jsmoove888', 'manonthemount', 'guyontheinternet2000', 'RealButtMash', 'Estulticio', 'Catmasteryip', 'towndrunk00', 'davidgr33n3', 'satanshelpdesk', 'sableee', 'ASketchyLlama', 'Uknown1972', 'MidLinebacker49', 'jdkwak', 'AdiosCorea', 'chundermonkey74', 'jackmoopoo', 'kkkmw', 'harelk', 'Rhiannax3', 'MikeDeRebel', 'tvbusy', 'bernieyee', 'chewkeat', 'savemysoul88', 'Kesher123', 'g0ldenb0y', 'GoodJobNL', 'Legacy03', 'Luke050715', 'Mr-Darkseid', 'joeDUBstep', 'lancer2238', 'the_random_bot', 'Salty_Assassin', 'BSTUFUI', 'ishidayamato', 'three_oneFour', 'valdici', 'Fighter754', 'Actuated_', 'augustm', 'BleuPrince', 'cotopaxi64', 'CosmicBioHazard', 'accidental_superman', 'whiskey547', 'Maklarr4000', 'katotaka', 'cantorock6', 'veekm', 'Nakjibokkeum', 'CatstructorPenny', 'AGRisator', 'ThoughtfulJanitor', 'KachangSorbet', 'Nichchk', 'jiggel_x', 'starfallg', 'Alchemist_XP', 'DimSumLee', 'Fidel_Costco', 'roostwrinchains', 'Ijustice', 'blacksungod', 'BaGamman', 'QuincyAzrael', 'bloncx', 'MAGA_ManX', 'Chaipod', 'pancake_ass', 'carlostsang', 'Dioxbit', 'namgwa', 'Jurk_McGerkin', 'DatMeme21', 'steve9341', 'SavedMountain', 'Darkblade48', 'SNR_1337', 'somebodyelse1889', 'BosWandeling', 'Verhaz', 'ItzJustMonika__', 'MaxImageBot', 'SumakQawsay', 'puppysayswoef', 'GabrielXiao', 'data_citizen', 'Cosmogally', 'NoHalf9', 'hazaface', 'aaclavijo', 'ZZ34', 'mindsnare1', 'sec5', 'MrNewVegas123', 'HonkinSriLankan', 'ChristianKS94', 'Jaedos', 'Defiyance', 'nametemplate', 'link-quizas', 'furnimal', 'mikibov', 'fapfairy22', 'Murdock07', 'Eddie_gaming', 'Wendfina', 'atomician', 'sleshm', 'zerou69', 'skejfee', 'LumpySpaceBrotha', 'smellslikeautism', 'Misko187', 'HyperMeems', 'lambopanda', 'FernadoPoo', 'lebrian', 'NeuroButt', 'KKLHY', 'JaJaWa', 'AHK403YYC', 'throwburgeratface', 'Charlie026', 'griftylifts', 'zhykonrx79', 'MelodySnow', 'ahx-fos3', 'kazalaa', 'PM_ME_SEXY_LOBSTERS', 'under_thesun', 'Markovspiron', 'Fonze1973', 'flamespear', 'miss_wolverine', 'HeliaXDemoN', 'B3n7340', 'Ahum-wait-what', 'isiyouji', 'justwalk1234', 'RageBill', '22_hours_ago', 'panchovilla_', 'overachiever', 'lukemcadams', 'C115551', 'Parallelism09191989', 'thisiscotty', 'jupiter1_', 'You_are_OK_Buddy', 'antoinedodson_', 'SgtShephard', 'EDGYhooDIE69', 'DnEng', 'deuceman4life', 'LonelyExchange', 'heylookasign', 'StanleyOpar', 'MistyMystery', 'bortalizer93', 'Karloman314', 'addictiontoprotein', 'BeijingTurkey', 'fossdell', 'rankinrez', 'Vodkacannon', 'mrkuolematon', 'Valencia335', 'wlekin', 'Unattributabledk', 'seoul2014', 'macanesedog', 'Electroyote', 'ancientflowers', 'challengingviews', 'jaqueburn', 'benjaminovich', 'Redguy05', 'Ahlruin', '04FS', 'davidmobey', 'ginesaisquoi', 'PG14_', 'Charlie_Yu', 'Francischew_zh', 'hav0cbl00d', 'HrOlympios', 'Micullen', 'Dr00dy', 'darps', 'Skelelight', 'Dude_JK', 'Mr-Rasta-Panda', 'bloopy1545', 'Raimondi06', 'invigo79', 'xX_ArsonAverage_Xx', 'tinhtinh'}
    new_list = list(new_set)
    two_set = {'iammrh4ppy', 'tongyaop', 'JanjaRobert', 'Charlie_Yu', 'nahcekimcm', 'Magitechnitive', 'hungzai', 'tQto', 'ravenraven173', 'Unattributabledk', 'Tunago_', 'percy_jones', 'Edinedi', 'ayavvv', 'omgplzdontkillme', 'simbaragdoll', 'sukieniko', 'PrometheusBoldPlan', 'holangjai', '2019titty_bear', 'thumper99', 'juddshanks', 'c00l105', 'storjfarmer', 'pertmax', 'essex_ludlow', 'plastic17', 'CormAlan', 'htc922', 'TravelPhoenix', 'stevegonzales1975', 'kingmoobot', 'baked-noodle', '8thDegreeSavage', 'Davekd', 'charliegrs', '[deleted]', 'CloroxEnergyDrink_', 'chibiwong', 'Sheldonleemyers', 'loromente', 'Xayacota', 'thematchalatte', 'Frokenfrigg', 'victurchen', 'GrassTastesGrass', 'NormenYu', 'rentonwong', 'deadon9'}
    two_list = list(two_set)
    fake_list = ['fake_account_1', 'fake_account_2', 'fake_account_3', 'fake_account_4', 'fake_account_5', 'fake_account_6', 'fake_account_7', 'fake_account_8', 'fake_account_9', 'fake_account_10', 'fake_account_11', 'fake_account_12', 'fake_account_13', 'fake_account_14', 'fake_account_15', 'fake_account_16', 'fake_account_17', 'fake_account_18', 'fake_account_19', 'fake_account_20', 'fake_account_21', 'fake_account_22', 'fake_account_23', 'fake_account_24', 'fake_account_25', 'fake_account_26', 'fake_account_27', 'fake_account_28', 'fake_account_29', 'fake_account_30', 'fake_account_31', 'fake_account_32', 'fake_account_33', 'fake_account_34', 'fake_account_35', 'fake_account_36', 'fake_account_37', 'fake_account_38', 'fake_account_39', 'fake_account_40', 'fake_account_41', 'fake_account_42', 'fake_account_43', 'fake_account_44', 'fake_account_45', 'fake_account_46', 'fake_account_47', 'fake_account_48', 'fake_account_49', 'fake_account_50', 'fake_account_51', 'fake_account_52', 'fake_account_53', 'fake_account_54', 'fake_account_55', 'fake_account_56', 'fake_account_57', 'fake_account_58', 'fake_account_59', 'fake_account_60', 'fake_account_61', 'fake_account_62', 'fake_account_63', 'fake_account_64', 'fake_account_65', 'fake_account_66', 'fake_account_67', 'fake_account_68', 'fake_account_69', 'fake_account_70', 'fake_account_71', 'fake_account_72', 'fake_account_73', 'fake_account_74', 'fake_account_75', 'fake_account_76', 'fake_account_77', 'fake_account_78', 'fake_account_79', 'fake_account_80', 'fake_account_81', 'fake_account_82', 'fake_account_83', 'fake_account_84', 'fake_account_85', 'fake_account_86', 'fake_account_87', 'fake_account_88', 'fake_account_89', 'fake_account_90', 'fake_account_91', 'fake_account_92', 'fake_account_93', 'fake_account_94', 'fake_account_95', 'fake_account_96', 'fake_account_97', 'fake_account_98', 'fake_account_99', 'fake_account_100']
    # query api for one month and add attack
    aug_karma_list = ['ZWF0cHVzc3k', 'ticonderoga67', 'Charlie_Yu', 'smallheartcocopop', 'ivan_422', 'glycerethe', 'NotEvenAMinuteMan', 'caandjr', 'fareastern44', 'suitandcry', 'Dynamic-Overlord', 'qlung', 'AuregaX', 'nahcekimcm', 'fusilli_jerry', 'GeneralAgent7', 'Tc0008', 'rustyrocky', 'IPromiseIWont', 'canto-ling', 'lifteroomang', 'MistyMystery', 'KoKansei', 'On9On9Laowai', 'UnagiTamaDon', 'Eat_the_Path', 'asianhipppy', 'chikochi', 'buttersismyname', '_relationship_', 'Ozhav', 'HKongBosGirl', 'blek_blek', '22witch22', 'holangjai', 'ScottThorson', 'investmentwanker0', 'KinnyRiddle', 'thepkboy', 'MrNewVegas123', 'LonelyMustard', 'justwalk1234', 'FATconTROLLah', 'tiangong', 'fefewhale', 'EverythingIsNorminal', 'LibertyTerp', 'adz4309', 'observer314159265']
    may_karma_list = ['Poison_Penis', 'HKnational', 'sampunk', 'magnusjonsson', 'loadofthewing', 'Koverp', 'jesselikesboys', 'sonastyinc', 'NotEvenAMinuteMan', 'CAF00187', 'mod83', 'Xelium23', 'derryainsworth', 'pelicane136', 'malak_oz', 'dfnsvguy', 'pointofgravity', 'Haruto-Kaito', 'Briganne', 'isaacng1997', 'spacecatbiscuits', 'On9On9Laowai', '5dorralovelongtime', 'HKtechTony', 'KoyaBot', 'zelda2wasEasy', 'whateverhk', 'thumper99', 'BrawlProdigy', 'Charlie_Yu']
    jun_karma_list = ['HKGong', 'lifteroomang', 'dfnsvguy', 'weddle_seal', 'HKnational', 'IosueYu', 'spacecatbiscuits', 'yc_hk', 'adz4309', 'chairmanwumao', 'iamgarron', 'sampunk', 'SuperSeagull01', 'fefewhale', 'yukiiiiii2008', 'wha2les', '8thDegreeSavage', 'thumper99', 'armored-dinnerjacket', 'chlpsc', 'Longsheep', 'EDoric', 'tableblue07', 'ZeroFPS_hk', 'magnusjonsson']
    july_karma_list = ['jvmesalexander', 'phy361sm', 'isaacng1997', 'adz4309', 'KeepLickingHoney', '7chut7', 'LiveForPanda', 'savemysoul88', 'NotEvenAMinuteMan', 'Surfingblue90', 'magnusjonsson', 'kharnevil', 'O7GS', 'ZWF0cHVzc3k', 'hkisdying', 'EDoric', 'leethal59', 'IPromiseIWont', 'adeveloper2', 'thumper99', 'hotasianman', 'yc_hk', 'netok', 'GottJager', 'fruitspunch-samurai', 'me-i-am', 'thanosbutt', 'ethenlau88', 'Techqjo', 'spicednut', 'KvasirsBlod', 'hellocheeseee', 'Mashmalo', 'oliver_reade', 'Davidier', 'yyl2000', 'sikingthegreat1', 'XPGamingYT', 'Brereddit112', 'Valyris', 'WikiTextBot', 'chairmanwumao', 'goocho', 'drkpua', 'KnowingRecipient', 'dhdhk', 'HKGong', 'drs43821']
    sep_karma_list = ['miss_wolverine', 'Moskau50', 'TravelPhoenix', 'scaur', 'BleuPrince', 'barson2408', 'mma21x', 'puppysayswoef', 'ZWF0cHVzc3k', 'Charlie_Yu', 'aaclavijo', 'thematchalatte', 'Kingmundo', 'GlobTrotters', 'ticonderoga67', 'joker_wcy', 'Breshawnashay', 'kspastroivanc', 'KnowingRecipient', 'Ihavenofork', 'monkeypie1234', 'Edinedi', 'kwanting', 'WonderfulPaterful1', 'suziewrong', 'Jerk_Alex', 'ishidayamato', 'pzivan', 'BitterEngineer', 'PmMeUrCreativity', 'gattaca_now', 'ocean_life_', 'ambitchouswannabe', 'NotEvenAMinuteMan', 'SubjectObjective', 'mitrang', 'notmycharmander', 'cyber_rigger']
    oct_karma_list = ['miss_wolverine', 'bloncx', 'scaur', 'TheTigerOfHK', 'brah888', 'eleinamazing', 'A_boy_and_his_boston', 'lebbe', 'GlobTrotters', 'Nichchk', 'hellobutno', 'Moskau50', 'Turd111', 'RogueSexToy', 'Blackhk', '22_hours_ago', 'humanity_is_doomed', 'ASketchyLlama', 'leftrighttopdown', 'IronKanabo', 'ZWF0cHVzc3k', 'simian_ninja', 'Eitoku_K', 'pomelopomelo']
    # total_list = aug_karma_list + may_karma_list + jun_karma_list + july_karma_list + sep_karma_list + oct_karma_list
    # gangdu_dic = collections.Counter(total_list)
    # print(gangdu_dic)
    user_graph, weight_dict, id_user_dic = query_api("2019-07-01", 30, 10000, july_karma_list)
    weight_edges = [(x, y, val) for (x, y), val in weight_dict.items()]
    user_graph.add_weighted_edges_from(weight_edges)
    print("******************defense partition************")
    print("origin node" + str(len(user_graph.nodes())))
    print("origin edge" + str(len(user_graph.edges())))
    community1 = community.best_partition(user_graph)
    origin_dic_lst = count_community(community1)
    print(origin_dic_lst)
    nx.write_gml(user_graph, "m4_july_defense.gml")
    # july_final_karma = fake_list + july_karma_list

    # defense_graph = user_graph
    # defense_weight_dict = counter_attack(weight_dict, july_final_karma)
    # weight_edges_defense = [(x, y, val) for (x, y), val in defense_weight_dict.items()]
    # defense_graph.add_weighted_edges_from(weight_edges_defense)
    # print("******************Defense********************")
    # print("defense_node" + str(len(defense_graph.nodes())))
    # print("defense_edge" + str(len(defense_graph.edges())))
    # defense_community = community.best_partition(defense_graph)
    # dic_lst = count_community(defense_community)
    # print(dic_lst)
    # nx.write_gml(defense_graph, "m3_july_defense_2.gml")
    #
    #
    # # attack
    # july_attack_graph = user_graph
    # july_attack_dict = attack(weight_dict, july_final_karma)
    # weight_edges_attack = [(x, y, val) for (x, y), val in july_attack_dict.items()]
    # july_attack_graph.add_weighted_edges_from(weight_edges_attack)
    # print("******************Attack*******************")
    # print("attack_node" + str(len(july_attack_graph.nodes())))
    # print("attack_edge" + str(len(july_attack_graph.edges())))
    # attack_community = community.best_partition(july_attack_graph)
    # attack_dic_lst = count_community(attack_community)
    # print(attack_dic_lst)
    # nx.write_gml(july_attack_graph, "m3_july_attack_2.gml")

    # # # partition counter attack
    # # w_dict = counter_attack(fake_list, weight_dict)
    # # weight_dict_attack = attack(weight_dict, oct_final_karma)






    # attack_graph = nx.read_gml("m3_oct_attack.gml")
    # part3 = community.best_partition(attack_graph)
    # origin_graph = nx.read_gml("m2_aug.gml")
    # part1 = community.best_partition(origin_graph)
    # defense_graph = nx.read_gml("m3_oct_defense.gml")
    # part2 = community.best_partition(defense_graph)
    # print(count_community(part3))
























