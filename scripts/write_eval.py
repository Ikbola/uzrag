import json
from pathlib import Path

EVAL_PATH = Path("data/eval.jsonl")

pairs = [
    {
        "question": "Tasavvufda tariqat nima?",
        "answer": "Tariqat — tirikchilikning barcha tashvishlaridan voz kechish hamda ixtiyorni pir-murshidga topshirib, poklanish yoʻlida uning koʻrsatmalariga amal qilish.",
        "chunk_index": 496,
        "book": "Adabiyot. 10-sinf (2022, Z.Mirzayeva, K.Jalilov)",
        "page": 150,
        "section": None
    },
    {
        "question": "\"Iliada\" va \"Odisseya\" dostonlari kimga tegishli?",
        "answer": "Afsonaviy shoir Homerga tegishli.",
        "chunk_index": 110,
        "book": "Adabiyot. 10-sinf (2022, Z.Mirzayeva, K.Jalilov)",
        "page": 33,
        "section": None
    },
    {
        "question": "Tirik organizmlar tomonidan modda va energiyaning oʻzlashtirilishi nima deyiladi?",
        "answer": "Oziqlanish.",
        "chunk_index": 1221,
        "book": "Biologiya. 10-sinf (2017, J.Tolipova, M.Umaraliyev)",
        "page": 64,
        "section": "13"
    },
    {
        "question": "Riboza va dezoksiriboza qaysi birikmalar tarkibiga kiradi?",
        "answer": "Nuklein kislotalar va ATF tarkibiga kiradi.",
        "chunk_index": 1086,
        "book": "Biologiya. 10-sinf (2017, J.Tolipova, M.Umaraliyev)",
        "page": 20,
        "section": "5"
    },
    {
        "question": "\"Robinzon Kruzo\" romanining muallifi kim?",
        "answer": "Ingliz adibi Daniyel Defo.",
        "chunk_index": 620,
        "book": "Adabiyot. 10-sinf (2022, Z.Mirzayeva, K.Jalilov)",
        "page": 193,
        "section": None
    },
    {
        "question": "Oʻrta asrlar va Uygʻonish davri jahon adabiyoti qaysi asrlarni oʻz ichiga oladi?",
        "answer": "V-XVI asrlarni oʻz ichiga oladi.",
        "chunk_index": 388,
        "book": "Adabiyot. 10-sinf (2022, Z.Mirzayeva, K.Jalilov)",
        "page": 117,
        "section": None
    },
    {
        "question": "Turkiston Muxtoriyatini kim tor-mor qilgan?",
        "answer": "Qizil gvardiyachilar va dashnoqlar tomonidan tor-mor qilingan.",
        "chunk_index": 1906,
        "book": "Oʻzbekiston tarixi. 10-sinf (2017, Q.Rajabov, A.Zamonov)",
        "page": 17,
        "section": None
    },
    {
        "question": "Don Kixot nimaga berilib ketib, ov va xoʻjalik ishlarini yigʻishtirib qoʻygan?",
        "answer": "Ritsarlar tavsif qilingan kitoblarni oʻqishga berilib ketgan.",
        "chunk_index": 413,
        "book": "Adabiyot. 10-sinf (2022, Z.Mirzayeva, K.Jalilov)",
        "page": 126,
        "section": None
    },
    {
        "question": "Gen muhandisligi qanday muammoni hal etishga qaratilgan?",
        "answer": "Insonlarning oziq-ovqatga boʻlgan ehtiyojini qondirishga qaratilgan nazariy va amaliy muammolarni hal etishga qaratilgan.",
        "chunk_index": 1033,
        "book": "Biologiya. 10-sinf (2017, J.Tolipova, M.Umaraliyev)",
        "page": 6,
        "section": "1"
    },
    {
        "question": "XX asr 80-yillari Oʻzbekiston qishloq xoʻjaligida qancha pestitsid ishlatilgan?",
        "answer": "90 000 tonna pestitsidlar ishlatilgan.",
        "chunk_index": 2275,
        "book": "Oʻzbekiston tarixi. 10-sinf (2017, Q.Rajabov, A.Zamonov)",
        "page": 124,
        "section": None
    },
    {
        "question": "Modernizm adabiyot va sanʼatda qanday paydo boʻlgan?",
        "answer": "Ijodiy izlanishlar natijasida turli xil oqimlarni birlashtirgan yangi yoʻnalish sifatida paydo boʻlgan.",
        "chunk_index": 883,
        "book": "Adabiyot. 10-sinf (2022, Z.Mirzayeva, K.Jalilov)",
        "page": 279,
        "section": None
    },
    {
        "question": "Turkiston Muxtoriyati hukumati qachon va qayerda tashkil topgan?",
        "answer": "1917-yil 26-28-noyabrda Qoʻqon shahrida Butunturkiston oʻlka musulmonlarining favqulodda IV qurultoyida tashkil topgan.",
        "chunk_index": 1896,
        "book": "Oʻzbekiston tarixi. 10-sinf (2017, Q.Rajabov, A.Zamonov)",
        "page": 14,
        "section": None
    },
    {
        "question": "Kurtaklanib koʻpayish qaysi organizmlarda kuzatiladi?",
        "answer": "Gʻovak tanlilarda, kovakichlilarda va ayrim halqali chuvalchanglarda kuzatiladi.",
        "chunk_index": 1236,
        "book": "Biologiya. 10-sinf (2017, J.Tolipova, M.Umaraliyev)",
        "page": 68,
        "section": "14"
    },
    {
        "question": "\"Goʻroʻgʻli\" turkum dostonlarini qanday guruhlarga boʻlish mumkin?",
        "answer": "Ikki katta guruhga: gʻarbiy guruh (Kavkaz, Yaqin va Oʻrta Sharq xalqlari) va sharqiy guruh (Markaziy Osiyo xalqlari).",
        "chunk_index": 29,
        "book": "Adabiyot. 10-sinf (2022, Z.Mirzayeva, K.Jalilov)",
        "page": 13,
        "section": None
    },
    {
        "question": "Jadid adabiyotining asosiy gʻoyalari qanday boʻlgan?",
        "answer": "Xalqni maʼrifatli qilish, tengsizlik va adolatsizlik hukmron tuzumdan xalos boʻlish, mustaqillikni qoʻlga kiritish va oʻzligini anglash.",
        "chunk_index": 709,
        "book": "Adabiyot. 10-sinf (2022, Z.Mirzayeva, K.Jalilov)",
        "page": 227,
        "section": None
    },
    {
        "question": "Bolsheviklar Qoʻqonga qanday harbiy kuchlar yuborgan?",
        "answer": "Ye.Perfilev boshchiligidagi piyoda, otliq va artilleriya qismlaridan iborat 11 eshelon yuborilgan.",
        "chunk_index": 1909,
        "book": "Oʻzbekiston tarixi. 10-sinf (2017, Q.Rajabov, A.Zamonov)",
        "page": 18,
        "section": None
    },
    {
        "question": "Biokimyoviy mezon boʻyicha turlarning asosiy farqi nimada?",
        "answer": "Har bir tur uchun xos irsiy material (DNK, RNK) va hujayradagi oqsillarning sifati va miqdorining oʻziga xosligida.",
        "chunk_index": 1527,
        "book": "Biologiya. 10-sinf (2017, J.Tolipova, M.Umaraliyev)",
        "page": 149,
        "section": "35"
    },
    {
        "question": "\"Tur\" atamasini sistematik birlik sifatida fanga kim kiritgan?",
        "answer": "Ingliz botanigi Djon Rey.",
        "chunk_index": 1522,
        "book": "Biologiya. 10-sinf (2017, J.Tolipova, M.Umaraliyev)",
        "page": 148,
        "section": "35"
    },
    {
        "question": "1906-yilda U. Betson va K. Pennet qanday kashfiyot qilgan?",
        "answer": "Xushboʻy hidli noʻxat oʻsimliklarini chatishtirib, belgilarning mustaqil holda irsiylanishi barcha belgilar uchun xos emasligini aniqlashgan.",
        "chunk_index": 1306,
        "book": "Biologiya. 10-sinf (2017, J.Tolipova, M.Umaraliyev)",
        "page": 88,
        "section": "18"
    },
    {
        "question": "Turlararo yashash uchun kurashga misol keltiring.",
        "answer": "Avstraliyaga Yevropadan olib kelingan oddiy ari nayzasi yoʻq kichik mahalliy arini siqib chiqargan; kulrang kalamush qora kalamushni siqib chiqara boshlagan.",
        "chunk_index": 1629,
        "book": "Biologiya. 10-sinf (2017, J.Tolipova, M.Umaraliyev)",
        "page": 177,
        "section": "41"
    },
    {
        "question": "Mendel gametalar sofligi farazini qanday asoslab bergan?",
        "answer": "F1 avlodda retsessiv belgilarning namoyon boʻlmasligi, F2 da esa dominant belgili bilan bir qatorda retsessiv belgili organizmlar hosil boʻlishini tahlil qilib asoslab bergan.",
        "chunk_index": 1289,
        "book": "Biologiya. 10-sinf (2017, J.Tolipova, M.Umaraliyev)",
        "page": 83,
        "section": "16"
    },
    {
        "question": "Irsiy kasalliklarni oʻrganish qaysi fanlar bilan bogʻliq?",
        "answer": "Gen muhandisligi va biotexnologiya sohalari bilan uzviy bogʻliq.",
        "chunk_index": 1034,
        "book": "Biologiya. 10-sinf (2017, J.Tolipova, M.Umaraliyev)",
        "page": 6,
        "section": "1"
    },
    {
        "question": "1926-yilda Oʻzbekiston SSRda qanday maʼmuriy oʻzgarishlar boʻlgan?",
        "answer": "7 ta viloyat, 23 ta uyezd, 241 ta volost va 1163 ta qishloq jamoasi oʻrniga yangi boʻlinish oʻtkazilib, 10 ta okrug tashkil etilgan.",
        "chunk_index": 2046,
        "book": "Oʻzbekiston tarixi. 10-sinf (2017, Q.Rajabov, A.Zamonov)",
        "page": 57,
        "section": None
    },
    {
        "question": "Hasharotlar yordamida changlanadigan oʻsimliklar gulining tuzilishi nima uchun turgun?",
        "answer": "Oʻsimliklar va ularni changlatuvchilarning birgalikdagi evolutsiyasi bilan bogʻliq.",
        "chunk_index": 1643,
        "book": "Biologiya. 10-sinf (2017, J.Tolipova, M.Umaraliyev)",
        "page": 181,
        "section": "42"
    },
    {
        "question": "Darvin moslanishlarning kelib chiqishini qanday tushuntirgan?",
        "answer": "Tashqi muhitning muayyan sharoitida organizmlardagi moslanishlar tabiiy tanlanish orqali paydo boʻlganligini ilmiy asosda tushuntirib bergan.",
        "chunk_index": 1670,
        "book": "Biologiya. 10-sinf (2017, J.Tolipova, M.Umaraliyev)",
        "page": 189,
        "section": "43"
    },
    {
        "question": "Sunʼiy tanlashda insonlar qanday maqsadlarni koʻzlaydi?",
        "answer": "Iqtisodiy, xoʻjalik va estetik talablarni qondirish maqsadlarini koʻzlaydi.",
        "chunk_index": 1600,
        "book": "Biologiya. 10-sinf (2017, J.Tolipova, M.Umaraliyev)",
        "page": 167,
        "section": "39"
    },
    {
        "question": "Poliploid turlar qayerda koʻp tarqalgan?",
        "answer": "Oʻsimliklar olamida koʻp tarqalgan; hayvon turlari orasida juda kam uchraydi.",
        "chunk_index": 1616,
        "book": "Biologiya. 10-sinf (2017, J.Tolipova, M.Umaraliyev)",
        "page": 172,
        "section": "40"
    },
    {
        "question": "Populatsiya toʻlqini nimalar tufayli yuz beradi?",
        "answer": "Harorat, namlik, yorugʻlikning mavsumiy oʻzgarishi, oziq miqdorining koʻp yoki oz boʻlishi va tabiiy ofatlar tufayli yuz beradi.",
        "chunk_index": 1545,
        "book": "Biologiya. 10-sinf (2017, J.Tolipova, M.Umaraliyev)",
        "page": 154,
        "section": "35"
    },
    {
        "question": "Xlorofill tarkibida qaysi element bor?",
        "answer": "Magniy.",
        "chunk_index": 1066,
        "book": "Biologiya. 10-sinf (2017, J.Tolipova, M.Umaraliyev)",
        "page": 15,
        "section": "3"
    },
    {
        "question": "Gemoglobin tarkibida qaysi element mavjud?",
        "answer": "Temir.",
        "chunk_index": 1066,
        "book": "Biologiya. 10-sinf (2017, J.Tolipova, M.Umaraliyev)",
        "page": 15,
        "section": "3"
    },
    {
        "question": "Milliy respublikalar tuzish gʻoyasi nimalar bilan asoslangan?",
        "answer": "Turkistondagi tub xalqlar hayotida tengsizlik mavjudligi va milliy mojarolar kuchayib borayotgani bilan asoslangan.",
        "chunk_index": 2026,
        "book": "Oʻzbekiston tarixi. 10-sinf (2017, Q.Rajabov, A.Zamonov)",
        "page": 51,
        "section": None
    },
    {
        "question": "1931-yilda Oʻzbekistonda quloqlarga qarshi qanday choralar koʻrilgan?",
        "answer": "3828 ta quloq xoʻjaliklari tugatilgan, 3871 xoʻjalik Ukraina, Sibir va Shimoliy Kavkazga surgun qilingan.",
        "chunk_index": 2073,
        "book": "Oʻzbekiston tarixi. 10-sinf (2017, Q.Rajabov, A.Zamonov)",
        "page": 65,
        "section": None
    },
    {
        "question": "\"Paxta ishi\" tergov guruhiga kimlar rahbarlik qilgan?",
        "answer": "T.X.Gdlyan va N.V.Ivanov rahbarlik qilgan.",
        "chunk_index": 2289,
        "book": "Oʻzbekiston tarixi. 10-sinf (2017, Q.Rajabov, A.Zamonov)",
        "page": 129,
        "section": None
    },
    {
        "question": "\"Ilohiy komediya\" dostonining muallifi kim?",
        "answer": "Buyuk italyan shoiri Dante Aligyeri.",
        "chunk_index": 402,
        "book": "Adabiyot. 10-sinf (2022, Z.Mirzayeva, K.Jalilov)",
        "page": 121,
        "section": None
    },
    {
        "question": "Uygʻonish davrining muhim xususiyatlaridan biri nima boʻlgan?",
        "answer": "Antik davr merosiga qiziqishning kuchayishi.",
        "chunk_index": 402,
        "book": "Adabiyot. 10-sinf (2022, Z.Mirzayeva, K.Jalilov)",
        "page": 121,
        "section": None
    },
    {
        "question": "Jan Jak Russo qaysi asarida tarbiya masalalarini yoritgan?",
        "answer": "\"Emil, yaʼni tarbiya haqida\" asarida.",
        "chunk_index": 620,
        "book": "Adabiyot. 10-sinf (2022, Z.Mirzayeva, K.Jalilov)",
        "page": 193,
        "section": None
    },
    {
        "question": "Interfazada S davri qancha davom etadi?",
        "answer": "Bir necha minutdan (bakteriyalarda) 6-7 soatgacha (sutemizuvchilarda) davom etadi.",
        "chunk_index": 1186,
        "book": "Biologiya. 10-sinf (2017, J.Tolipova, M.Umaraliyev)",
        "page": 53,
        "section": "11"
    },
    {
        "question": "Filoembriogenez nazariyasini kim ishlab chiqqan?",
        "answer": "Rus olimi A.M. Seversov.",
        "chunk_index": 1716,
        "book": "Biologiya. 10-sinf (2017, J.Tolipova, M.Umaraliyev)",
        "page": 203,
        "section": "45"
    },
    {
        "question": "Don Kixotga ritsarlik unvonini kim bergan?",
        "answer": "Qovoqxona xoʻjayini bergan.",
        "chunk_index": 431,
        "book": "Adabiyot. 10-sinf (2022, Z.Mirzayeva, K.Jalilov)",
        "page": 130,
        "section": None
    },
    {
        "question": "Shoahmad Shomahmudov oilasi urush yillarida nima qilgan?",
        "answer": "Koʻpchilikka ibrat boʻlib, boshqa xalqlarning bolalarini oʻz oilasiga qabul qilgan.",
        "chunk_index": 2175,
        "book": "Oʻzbekiston tarixi. 10-sinf (2017, Q.Rajabov, A.Zamonov)",
        "page": 94,
        "section": None
    },
]

EVAL_PATH.parent.mkdir(parents=True, exist_ok=True)
with EVAL_PATH.open("w", encoding="utf-8") as fh:
    for p in pairs:
        fh.write(json.dumps(p, ensure_ascii=False) + "\n")

print(f"wrote {len(pairs)} eval pairs -> {EVAL_PATH}")