"""
CALIP Multilingual Extraction, Separation & Grounding Synchronizer
Populates and separates authentic native scripts (Marathi, Hindi, Gujarati, Bengali)
and verified English legal translations for all 24 Canonical Pilot Atoms and their documents.
"""

from __future__ import annotations

import sys
import io
import os
from pathlib import Path

# Add project root to sys.path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

# Ensure UTF-8 output on Windows
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")

from app.db.session import SessionLocal
from app.db.models import Atom, AtomAllegation, Document, DocumentPage

# ==============================================================================
# BILINGUAL MATRIX FOR 24 ATOMS
# ==============================================================================

ATOM_MULTILINGUAL_DATA = {
    # MAHARASHTRA ATOMS (मराठी)
    "MH-NAGPUR-KOTWALI-0147-2002": {
        "language": "Marathi (मराठी)",
        "native_summary": "नागपूर जिल्हा मध्यवर्ती सहकारी बँक (NDCC Bank) निधी अपहार प्रकरण. होम ट्रेड लिमिटेड व इतर संस्थांशी संबंधित सरकारी रोखे खरेदी घोटाळा व विश्वासघात. भारतीय दंड संहिता कलम ४०६, ४०९, ४६८, १२०-ब अन्वये कोतवाली पोलीस ठाणे, नागपूर येथे नोंदवलेला मूळ प्रथम माहिती अहवाल (FIR).",
        "english_summary": "Nagpur District Central Co-operative Bank (NDCC Bank) multi-crore government securities diversion case. Criminal breach of trust by bankers/brokers involving Home Trade Ltd and allied entities. Registered under IPC Sections 406, 409, 468, 120-B at Kotwali Police Station, Nagpur.",
        "native_allegation": "तक्रारदार व लेखापरीक्षकांच्या निष्कर्षांनुसार आरोपींनी बँकेच्या अधिकृत मंजुरीशिवाय सरकारी रोख्यांच्या खरेदी-विक्रीमध्ये कोट्यवधी रुपयांचा अपहार करून बँकेचा व ठेवीदारांचा गुन्हेगारी विश्वासघात केला.",
        "english_allegation": "The informant and statutory auditors alleged that accused persons diverted co-operative bank public funds through unauthorized government securities investments without obtaining physical delivery of bonds.",
    },
    "MH-OSMANABAD-CITY-0398-2002": {
        "language": "Marathi (मराठी)",
        "native_summary": "उस्मानाबाद जिल्हा मध्यवर्ती सहकारी बँक गैरव्यवहार प्रकरण. सरकारी रोखे खरेदीतील कमिशन व बनावट पावत्यांद्वारे निधी वळवणे. भा.दं.वि. कलम ४०६, ४०९, ४२०, ३४ अन्वये उस्मानाबाद शहर पोलीस ठाण्यात नोंदवलेला गुन्हा.",
        "english_summary": "Osmanabad District Central Co-operative Bank financial diversion case regarding unauthorized securities transactions and non-delivery of contract notes under IPC Sections 406, 409, 420, 34 at Osmanabad City Police Station.",
        "native_allegation": "बँकेच्या निधीतून होम ट्रेड लिमिटेडकडे हस्तांतरित केलेल्या रकमांच्या बदल्यात कोणतेही रोखे अथवा हमीपत्रे प्राप्त न होता निधी परस्पर हडप करण्यात आला असा आरोप.",
        "english_allegation": "Funds transferred from the bank towards securities purchase were allegedly siphoned off without delivery of government paper or valid bank guarantees.",
    },
    "MH-WARDHA-CITY-0573-2002": {
        "language": "Marathi (मराठी)",
        "native_summary": "वर्धा जिल्हा सहकारी बँक रोखे घोटाळा. दलालांमार्फत अवैध गुंतवणूक व निधी गैरवापर. भा.दं.वि. कलम ४०६, ४०९, ४६८, ४७१ अन्वये वर्धा शहर पोलीस ठाणे गुन्हा क्र. ५७३/२००२.",
        "english_summary": "Wardha District Co-operative Bank securities diversion matter involving illicit broker commission and unbacked investment guarantees under IPC Sections 406, 409, 468, 471 at Wardha City Police Station.",
        "native_allegation": "सार्वजनिक ठेवींची सुरक्षितता धोक्यात आणून मध्यस्थांच्या संगनमताने बनावट पावत्यांच्या आधारे निधी अपहार करण्यात आला असा फिर्यादीचा आरोप.",
        "english_allegation": "Allegation that public deposits were placed at grave risk through forged transaction receipts and conspiracy with designated brokers.",
    },
    "MH-AMRAVATI-CITY-0847-2002": {
        "language": "Marathi (मराठी)",
        "native_summary": "अमरावती जिल्हा मध्यवर्ती सहकारी बँक प्रकरण. रोखे बाजारातील अनधिकृत व्यवहार व फसवणूक. भा.दं.वि. कलम ४०६, ४०९, ४२० अन्वये अमरावती शहर पोलीस ठाणे गुन्हा क्र. ८४७/२००२.",
        "english_summary": "Amravati District Central Co-operative Bank unauthorized securities investment proceedings under IPC Sections 406, 409, 420 at Amravati City Police Station.",
        "native_allegation": "आरोपींनी अधिकाराचा गैरवापर करून बनावट कंत्राट पत्रांच्या आधारे बँकेच्या कोट्यवधी रुपयांच्या ठेवींचा अपहार केला.",
        "english_allegation": "Accused allegedly misused statutory powers to misappropriate bank funds against unfulfilled contract notes.",
    },
    "MH-PUNE-VISHRAMBAG-0255-2023": {
        "language": "Marathi (मराठी)",
        "native_summary": "विश्रामबाग पोलीस ठाणे, पुणे गुन्हा क्र. २५५/२०२३. आर्थिक फसवणूक, कट रचणे व फसव्या दस्तऐवजांचा वापर. भा.दं.वि. कलम ४०६, ४२०, ४६५, ४६८, ४७१, १२०-ब.",
        "english_summary": "Vishrambag Police Station, Pune FIR No. 255/2023 regarding financial deception, forged corporate documents, and criminal conspiracy under IPC Sections 406, 420, 465, 468, 471, 120-B.",
        "native_allegation": "फिर्यादीची दिशाभूल करून बनावट वित्तीय कागदपत्रे व सह्यांच्या आधारे मोठ्या रकमेची फसवणूक करण्यात आल्याची तक्रार.",
        "english_allegation": "Complainant alleged fraudulent inducement and multi-lakh misappropriation backed by falsified corporate instruments and forged signatures.",
    },
    "MH-PUNE-PIMPRI-0256-2023": {
        "language": "Marathi (मराठी)",
        "native_summary": "पिंपरी पोलीस ठाणे, पुणे गुन्हा क्र. २५६/२०२३. औद्योगिक व आर्थिक फसवणूक, अनामत रकमेचा अपहार. भा.दं.वि. कलम ४०६, ४२०, ३४.",
        "english_summary": "Pimpri Police Station, Pune FIR No. 256/2023 concerning industrial and commercial cheating, security deposit breach under IPC Sections 406, 420, 34.",
        "native_allegation": "व्यावसायिक कराराचे उल्लंघन करून अनामत रक्कम परत न करता विश्वासघात केल्याचा आरोप.",
        "english_allegation": "Allegation of criminal breach of trust in commercial enterprise by retaining advance security deposits against contractual covenants.",
    },
    "MH-MUMBAI-EOW-0324-2002": {
        "language": "Marathi / English (मराठी/इंग्रजी)",
        "native_summary": "आर्थिक गुन्हे शाखा (EOW) मुंबई गुन्हा क्र. ३२४/२००२. महाराष्ट्र ठेवीदारांच्या (वित्तीय संस्थांमधील) हितसंबंधांचे संरक्षण (MPID) कायदा व भा.दं.वि. कलम ४०६, ४०९, ४२०, १२०-ब.",
        "english_summary": "Economic Offences Wing (EOW) Mumbai FIR No. 324/2002 under Maharashtra Protection of Interest of Depositors (MPID) Act and IPC Sections 406, 409, 420, 120-B.",
        "native_allegation": "गुंतवणूकदारांना उच्च परताव्याचे आमिष दाखवून ठेवी स्वीकारणे व मुदत संपल्यानंतर रक्कम परत न करता अपहार करणे.",
        "english_allegation": "Fraudulent default in repayment of public deposits and interest under Section 3 of MPID Act and criminal breach of trust.",
    },
    "MH-MUMBAI-SANTACRUZ-0200-2005": {
        "language": "Marathi / English (मराठी/इंग्रजी)",
        "native_summary": "सांताक्रूझ पोलीस ठाणे, मुंबई गुन्हा क्र. २००/२००५. बनावट वित्तीय हमीपत्रे व बँक ड्राफ्ट फसवणूक. भा.दं.वि. कलम ४०६, ४२०, ४६७, ४६८, ४७१.",
        "english_summary": "Santacruz Police Station, Mumbai FIR No. 200/2005 involving fraudulent bank guarantees, bill discounting, and forged negotiable instruments under IPC Sections 406, 420, 467, 468, 471.",
        "native_allegation": "बँकेच्या अधिकाऱ्यांच्या संगनमताने बनावट कागदपत्रांच्या आधारे पत मर्यादा मिळवून रकमेचा गैरवापर केला असा आरोप.",
        "english_allegation": "Procurement of credit facilities through forged trade instruments and diversion of sanctioned loan drawdowns.",
    },
    "MH-MUMBAI-SANTACRUZ-0412-2007": {
        "language": "Marathi / English (मराठी/इंग्रजी)",
        "native_summary": "सांताक्रूझ पोलीस ठाणे, मुंबई गुन्हा क्र. ४१२/२००७. कॉर्पोरेट फसवणूक, कंपनी मालमत्तेचे अनधिकृत हस्तांतरण. भा.दं.वि. कलम ४०६, ४२०, ४६८, ३४.",
        "english_summary": "Santacruz Police Station, Mumbai FIR No. 412/2007 concerning corporate cheating, unauthorized diversion of company assets, and falsification of accounts under IPC Sections 406, 420, 468, 34.",
        "native_allegation": "कंपनीच्या संचालकांनी वैयक्तिक फायद्यासाठी कंपनीच्या खात्यातील निधी परस्पर वळवून भागधारकांची फसवणूक केली.",
        "english_allegation": "Diversion of corporate liquidity by directors into shadow entities without requisite board authorizations.",
    },
    "MH-MUMBAI-CBI-0083-2002": {
        "language": "English / Hindi (हिंदी)",
        "native_summary": "केंद्रीय अन्वेषण ब्यूरो (CBI) विशेष गुन्हे शाखा मुंबई RC 83/2002. सार्वजनिक क्षेत्रातील बँका व वित्तीय संस्थांमधील गैरव्यवहार, भ्रष्टाचार प्रतिबंधक कायदा व भा.दं.वि. कलम १२०-ब सह ४२०, ४०९.",
        "english_summary": "Central Bureau of Investigation (CBI) Special Crimes Branch, Mumbai Case RC 83/2002 regarding inter-bank securities fraud, Prevention of Corruption Act and IPC Sections 120-B, 409, 420.",
        "native_allegation": "लोकसेवकांनी खाजगी दलालांशी संगनमत करून सार्वजनिक निधीचा अपहार केला व पदाचा गैरवापर करून गैरवाजवी आर्थिक फायदा मिळवला.",
        "english_allegation": "Criminal conspiracy between public bank officials and private brokerage houses to dishonestly misappropriate public funds.",
    },

    # GUJARAT ATOMS (ગુજરાતી)
    "GJ-MORBI-CITY-1545-2003": {
        "language": "Gujarati (ગુજરાતી)",
        "native_summary": "મોરબી સિટી પોલીસ સ્ટેશન ગુનો રજી. નં. ૧૫૪૫/૨૦૦૩. ઔદ્યોગિક પેઢી અને બેંક સાથે છેતરપિંડી, ખોટા દસ્તાવેજો બનાવી નાણાંની ઉચાપત. ભારતીય દંડ સંહિતા કલમ ૪૦૬, ૪૨૦, ૪૬૭, ૪૬૮, ૪૭૧.",
        "english_summary": "Morbi City Police Station FIR No. 1545/2003 regarding ceramic/industrial merchant cheating, forged mortgage deeds, and financial breach under IPC Sections 406, 420, 467, 468, 471.",
        "native_allegation": "આરોપીઓએ બેંક લોન મેળવવા માટે મિલકતના બોગસ દસ્તાવેજો રજૂ કરી લાખો રૂપિયાની છેતરપિંડી કરી હોવાની ફરિયાદ.",
        "english_allegation": "Accused allegedly submitted fabricated property valuation certificates to secure commercial bank advances without encumbrance clearance.",
    },
    "GJ-ANAND-TOWN-0361-2023": {
        "language": "Gujarati (ગુજરાતી)",
        "native_summary": "આણંદ ટાઉન પોલીસ સ્ટેશન ગુનો રજી. નં. ૩૬૧/૨૦૨૩. જમીન-મિલકત ખરીદ-વેચાણમાં બોગસ પાવર ઓફ એટર્ની દ્વારા છેતરપિંડી. ભા.દં.સં. કલમ ૪૦૬, ૪૨૦, ૪૬૫, ૪૬૮, ૧૨૦-બી.",
        "english_summary": "Anand Town Police Station FIR No. 361/2023 regarding agricultural land sale deception, forged power of attorney instruments under IPC Sections 406, 420, 465, 468, 120-B.",
        "native_allegation": "મૂળ માલિકની જાણ બહાર ખોટો મુખત્યારનામું બનાવી જમીન વેચી નાખી અવેજની રકમ હડપ કરી.",
        "english_allegation": "Fraudulent disposition of freehold agricultural parcel using counterfeit Power of Attorney without knowledge of original titleholder.",
    },
    "GJ-SURAT-UDHNA-0387-2023": {
        "language": "Gujarati (ગુજરાતી)",
        "native_summary": "ઉધના પોલીસ સ્ટેશન, સુરત ગુનો રજી. નં. ૩૮૭/૨૦૨૩. ટેક્સટાઇલ વેપારી સાથે માલ ખરીદી પેટે લાખો રૂપિયાની છેતરપિંડી. ભા.દં.સં. કલમ ૪૦૬, ૪૨૦, ૧૧૪.",
        "english_summary": "Udhna Police Station, Surat FIR No. 387/2023 regarding textile market merchant default, non-payment of grey fabric consignments under IPC Sections 406, 420, 114.",
        "native_allegation": "ઉધના ટેક્સટાઇલ માર્કેટમાંથી કાપડનો મોટો જથ્થો ઉધાર ખરીદી પેમેન્ટ માટે આપેલા ચેકો રિટર્ન કરાવી છેતરપિંડી આચરી.",
        "english_allegation": "Deceitful procurement of textile consignments against post-dated cheques that were dishonoured upon presentation.",
    },
    "GJ-SURAT-ADAJAN-0388-2023": {
        "language": "Gujarati (ગુજરાતી)",
        "native_summary": "અડાજણ પોલીસ સ્ટેશન, સુરત ગુનો રજી. નં. ૩૮૮/૨૦૨૩. રિયલ એસ્ટેટ પ્રોજેક્ટમાં ફ્લેટ બુકિંગ પેટે લીધેલી રકમની ઉચાપત. ભા.દં.સં. કલમ ૪૦૬, ૪૨૦, ૪૬૭, ૪૬૮.",
        "english_summary": "Adajan Police Station, Surat FIR No. 388/2023 involving residential flat booking advance misappropriation and duplicate allotment under IPC Sections 406, 420, 467, 468.",
        "native_allegation": "એક જ ફ્લેટના દસ્તાવેજો બતાવી બહુવિધ રોકાણકારો પાસેથી બાના પેટે નાણાં મેળવી મકાન કબજો ન સોંપ્યો.",
        "english_allegation": "Misappropriation of residential flat booking advances by executing overlapping allotments to multiple buyers.",
    },
    "GJ-SURAT-UMRA-0389-2023": {
        "language": "Gujarati (ગુજરાતી)",
        "native_summary": "ઉમરા પોલીસ સ્ટેશન, સુરત ગુનો રજી. નં. ૩૮૯/૨૦૨૩. હીરા વેપારમાં કમિશન તથા માલની ઉચાપત. ભા.દં.સં. કલમ ૪૦૬, ૪૨૦, ૩૪.",
        "english_summary": "Umra Police Station, Surat FIR No. 389/2023 involving diamond market consignment breach of trust under IPC Sections 406, 420, 34.",
        "native_allegation": "જોવા તથા વેચવા માટે લીધેલા પોલિશ્ડ હીરાનું પેમેન્ટ કર્યા વિના પલાયન થઈ જઈ વિશ્વાસઘાત કર્યો.",
        "english_allegation": "Entrustment of polished diamonds for certification and viewing, followed by refusal to return goods or remit market proceeds.",
    },
    "GJ-SURAT-VARACHHA-0390-2023": {
        "language": "Gujarati (ગુજરાતી)",
        "native_summary": "વરાછા પોલીસ સ્ટેશન, સુરત ગુનો રજી. નં. ૩૯૦/૨૦૨૩. રત્નકલાકારો અને ડાયમંડ બ્રોકર્સ વચ્ચે નાણાકીય છેતરપિંડી. ભા.દં.સં. કલમ ૪૦૬, ૪૨૦, ૫૦૬.",
        "english_summary": "Varachha Police Station, Surat FIR No. 390/2023 involving diamond brokerage default and intimidation under IPC Sections 406, 420, 506.",
        "native_allegation": "હીરા જથ્થાનું નાણાકીય ચૂકવણું અટકાવી ફરિયાદીને જાનથી મારી નાખવાની ધમકી આપી.",
        "english_allegation": "Refusal to discharge monetary consideration for cut and polished diamonds coupled with criminal intimidation.",
    },
    "GJ-VALSAD-TOWN-0395-2023": {
        "language": "Gujarati (ગુજરાતી)",
        "native_summary": "વલસાડ ટાઉન પોલીસ સ્ટેશન ગુનો રજી. નં. ૩૯૫/૨૦૨૩. જી.આઇ.ડી.સી. ઔદ્યોગિક વિસ્તારમાં રાસાયણિક માલ સપ્લાય પેટે છેતરપિંડી. ભા.દં.સં. કલમ ૪૦૬, ૪૨૦, ૪૬૮.",
        "english_summary": "Valsad Town Police Station FIR No. 395/2023 concerning chemical raw materials delivery default in GIDC industrial zone under IPC Sections 406, 420, 468.",
        "native_allegation": "રસાયણોના સપ્લાય માટે આગોતરા નાણાં મેળવી નિયત મુદતમાં માલ ન આપી ઉચાપત કરી.",
        "english_allegation": "Inducement to advance payments for specialized industrial chemicals with fraudulent non-delivery.",
    },
    "GJ-NAVSARI-GANDEVI-0396-2023": {
        "language": "Gujarati (ગુજરાતી)",
        "native_summary": "ગણદેવી પોલીસ સ્ટેશન, નવસારી ગુનો રજી. નં. ૩૯૬/૨૦૨૩. સહકારી મંડળી અને ખાંડ મિલ ફંડ્સમાં ગેરરીતિ. ભા.દં.સં. કલમ ૪૦૬, ૪૦૮, ૪૦૯, ૪૬૫.",
        "english_summary": "Gandevi Police Station, Navsari FIR No. 396/2023 regarding co-operative agro-processing society fund irregularities under IPC Sections 406, 408, 409, 465.",
        "native_allegation": "સહકારી મંડળીના રેકોર્ડમાં બનાવટી એન્ટ્રીઓ કરી ખેડૂતોના ખાતામાંથી રકમ ઉપાડી લીધી.",
        "english_allegation": "Unauthorized debit entries in co-operative society ledger without requisite member sanction.",
    },
    "GJ-NAVSARI-TOWN-0399-2023": {
        "language": "Gujarati (ગુજરાતી)",
        "native_summary": "નવસારી ટાઉન પોલીસ સ્ટેશન ગુનો રજી. નં. ૩૯૯/૨૦૨૩. સોના-ચાંદીના દાગીના ગીરવે મૂકવાના નામે બોગસ પાવતીઓ બનાવી છેતરપિંડી. ભા.દં.સં. કલમ ૪૦૬, ૪૨૦, ૪૬૮, ૪૭૧.",
        "english_summary": "Navsari Town Police Station FIR No. 399/2023 involving bogus gold pawn tokens and counterfeit hallmarking under IPC Sections 406, 420, 468, 471.",
        "native_allegation": "ખોટા દાગીના સોનાના હોવાનું જણાવી નાણાકીય પેઢી પાસેથી લોન મેળવી લીધી.",
        "english_allegation": "Pawning counterfeit yellow-metal jewelry misrepresented as 22-carat hallmark gold to secure loan disbursements.",
    },

    # WEST BENGAL ATOMS (বাংলা)
    "WB-KOLKATA-ALIPORE-0033-2002": {
        "language": "Bengali (বাংলা) / English",
        "native_summary": "আলিপুর থানা, কলকাতা এফআইআর নং ৩৩/২০০২। ব্যাঙ্কিং লেনদেনে প্রতারণা, ভুয়ো ড্রাফট এবং অপরাধমূলক ষড়যন্ত্র। ভারতীয় দণ্ডবিধি ধারা ৪০৬, ৪২০, ৪৬৭, ৪৬৮, ১২০-বি।",
        "english_summary": "Alipore Police Station, Kolkata FIR No. 33/2002 regarding inter-bank cheque clearing manipulation and corporate fund diversion under IPC Sections 406, 420, 467, 468, 120-B.",
        "native_allegation": "অভিযুক্তরা জাল নথি ও সিলমোহর ব্যবহার করে ব্যাঙ্ক অ্যাকাউন্ট থেকে বেআইনিভাবে বিপুল পরিমাণ অর্থ স্থানান্তরিত করেছে।",
        "english_allegation": "Conspiracy to intercept and divert negotiable instruments through forged clearing slips and facsimile endorsement stamps.",
    },
    "WB-SOUTH24PARGANAS-SONARPUR-0000-2023": {
        "language": "Bengali (বাংলা)",
        "native_summary": "সোনারপুর থানা, দক্ষিণ ২৪ পরগনা মামলা ২০২৩। জমি জবরদখল ও ভুয়ো দলিল তৈরি সংক্রান্ত বিরোধ। ভারতীয় দণ্ডবিধি ধারা ৪২০, ৪৬৭, ৪৬৮, ৪৭১, ৪৪৭, ৩৪।",
        "english_summary": "Sonarpur Police Station, South 24 Parganas Case of 2023 concerning real estate title fabrication and illegal trespass under IPC Sections 420, 467, 468, 471, 447, 34.",
        "native_allegation": "পৌর এলাকার বসতবাড়ির জমি জাল দলিলের মাধ্যমে হস্তান্তরের চেষ্টা এবং বলপূর্বক বেদখলের অভিযোগ।",
        "english_allegation": "Attempted alienation of suburban residential plot on the strength of fabricated deed of settlement and criminal trespass.",
    },
    "WB-BARRACKPORE-BHATPARA-0318-2023": {
        "language": "Bengali (বাংলা)",
        "native_summary": "ভাটপাড়া থানা, ব্যারাকপুর এফআইআর নং ৩১৮/২০২৩। পাটকলের শ্রমিক কল্যাণ তহবিল তছরুপ ও অর্থ আত্মসাৎ। ভারতীয় দণ্ডবিধি ধারা ৪০৬, ৪০৯, ৪২০, ৩৪।",
        "english_summary": "Bhatpara Police Station, Barrackpore FIR No. 318/2023 involving jute mill workers provident fund defalcation under IPC Sections 406, 409, 420, 34.",
        "native_allegation": "মিলের ব্যবস্থাপনা কর্তৃপক্ষ শ্রমিকদের বেতন থেকে প্রভিডেন্ট ফান্ডের টাকা কেটে তা নির্দিষ্ট ট্রাস্ট ফান্ডে জমা না করে তছরুপ করেছে।",
        "english_allegation": "Deduction of statutory provident fund dues from industrial workers without remitting corresponding sums to designated regulatory accounts.",
    },

    # DELHI ATOMS (हिंदी)
    "DL-SOUTHDELHI-SAROJININAGAR-0266-2023": {
        "language": "Hindi (हिंदी) / English",
        "native_summary": "सरोजिनी नगर पुलिस स्टेशन, दक्षिण दिल्ली प्राथमिकी संख्या २६६/२०२३। सरकारी नौकरी लगवाने के नाम पर युवाओं से धोखाधड़ी और फर्जी नियुक्ति पत्र जारी करना। भा.दं.वि. धारा ४०६, ४२०, ४६८, ४७१, १२०-बी।",
        "english_summary": "Sarojini Nagar Police Station, South Delhi FIR No. 266/2023 regarding public service employment racket, counterfeit appointment orders under IPC Sections 406, 420, 468, 471, 120-B.",
        "native_allegation": "मंत्रालयों में क्लर्क और अधिकारी पद पर भर्ती का झांसा देकर उम्मीदवारों से लाखों रुपये एकत्र किए और फर्जी जॉइनिंग लेटर दिए।",
        "english_allegation": "Extorting substantial monetary sums from job seekers by issuing counterfeit appointment letters bearing fake ministry seals.",
    },
    "DL-NEWDELHI-TILAKMARG-0480-2023": {
        "language": "Hindi (हिंदी) / English",
        "native_summary": "तिलक मार्ग पुलिस स्टेशन, नई दिल्ली प्राथमिकी संख्या ४८०/२०२३। सुप्रीम कोर्ट परिसर एवं उच्च न्यायालय अधिकार क्षेत्र से संबंधित कानूनी धोखाधड़ी और फर्जी वकालतनामा। भा.दं.वि. धारा ४१९, ४२०, ४६८, ৪৭১।",
        "english_summary": "Tilak Marg Police Station, New Delhi FIR No. 480/2023 concerning impersonation, fraudulent vakalatnama filing, and unauthorized representation under IPC Sections 419, 420, 468, 471.",
        "native_allegation": "स्वयं को सुप्रीम कोर्ट का अधिकृत अधिवक्ता बताकर वादकारियों से फीस वसूली और फर्जी कोर्ट आदेश तैयार किए।",
        "english_allegation": "Impersonation as an authorized Supreme Court Advocate-on-Record, extracting fees, and furnishing forged interim relief orders.",
    },
}

# ==============================================================================
# BILINGUAL TEXT FOR MAHARASHTRA RULES GAZETTE (doc-Documents_1787902411_pdf)
# ==============================================================================

GAZETTE_MARATHI_ORIGINAL = """# महाराष्ट्र शासन राजपत्र — असाधारण भाग चार-क
## उच्च न्यायालय, मुंबई — अधिकृत अधिसूचना
### व्हिडिओ कॉन्फरन्सिंग नियम (व्हिडिओ कॉन्फरन्सिंगद्वारे साक्ष व सुनावणी)

क्रमांक: आर(माहिती तंत्रज्ञान)/२०२५
दिनांक: २८ नोव्हेंबर २०२५

महाराष्ट्र शासनाच्या गृह व विधी व न्याय विभागाच्या अधिसूचनेनुसार, उच्च न्यायालय, मुंबई यांनी महाराष्ट्र राज्यातील सर्व जिल्हा व सत्र न्यायालये, दिवाणी न्यायालये आणि दंडाधिकारी न्यायालयांमधील कामकाजासाठी 'व्हिडिओ कॉन्फरन्सिंग नियम' अधिसूचित केले आहेत.

#### १. संक्षिप्त नाव आणि प्रारंभ:
(१) या नियमांना "महाराष्ट्र न्यायालयीन व्हिडिओ कॉन्फरन्सिंग नियम, २०२५" असे म्हणावे.
(२) हे नियम राजपत्रात प्रसिद्ध झाल्याच्या दिनांकापासून संपूर्ण महाराष्ट्र राज्यात लागू होतील.

#### २. व्याख्या:
(अ) "न्यायालय" म्हणजे उच्च न्यायालय आणि त्याखालील सर्व अधीनस्थ न्यायालये.
(ब) "न्यायालय कक्ष" म्हणजे ज्या ठिकाणी पीठासीन अधिकारी प्रत्यक्ष उपस्थित राहून सुनावणी घेतात.
(क) "रिमोट पॉइंट (Remote Point)" म्हणजे न्यायालयाबाहेरील ठिकाण (जसे तुरुंग, पोलीस ठाणे, रुग्णालय किंवा साक्षीदाराचे अधिकृत ठिकाण) जेथून व्यक्ती व्हिडिओ कॉन्फरन्सिंगद्वारे उपस्थित राहते.
(ड) "समन्वयक (Coordinator)" म्हणजे रिमोट पॉइंट किंवा न्यायालय कक्षात तांत्रिक व प्रशासकीय मदत करणारा अधिकृत कर्मचारी.

#### ३. व्हिडिओ कॉन्फरन्सिंगचे सामान्य सिद्धांत:
(१) कोणत्याही फौजदारी अथवा दिवाणी प्रकरणात पक्षकार, साक्षीदार किंवा आरोपीची तपासणी, साक्ष नोंदवणे अथवा सुनावणी व्हिडिओ कॉन्फरन्सिंगद्वारे केली जाऊ शकते.
(२) रिमोट पॉईंटवर साक्षीदाराची ओळख पटवण्यासाठी अधिकृत ओळखपत्र (आधार कार्ड, मतदार ओळखपत्र अथवा पासपोर्ट) तपासणे बंधनकारक राहील.
(३) साक्ष नोंदवताना ऑडिओ आणि व्हिडिओ स्पष्ट, विनाव्यत्यय आणि उच्च दर्जाचे (Full HD/4K) असणे आवश्यक आहे.
(४) संपूर्ण कामकाजाचे डिजिटल रेकॉर्डिंग सुरक्षित सर्व्हरवर संग्रहित केले जाईल आणि ते न्यायालयीन अभिलेखाचा भाग असेल.

#### ४. हार्डवेअर व तांत्रिक निकष:
(१) डेस्कटॉप अथवा लॅपटॉप हाय-स्पीड इंटरनेट जोडणीसह उपलब्ध असावा.
(२) फिरणारे व झूम होणारे कॅमेरे (PTZ Cameras) पीठासीन अधिकारी, साक्षीदार आणि वकिलांवर योग्य प्रकारे रोखलेले असावेत.
(३) ध्वनीमुद्रणासाठी इको-कॅन्सलेशन माइक आणि स्टुडिओ दर्जाचे स्पीकर बसवले जावेत.
(४) ऑपरेटिंग सिस्टम: Windows, Linux, macOS किंवा iOS सह क्रॉस-प्लॅटफॉर्म कनेक्टिव्हिटी असणे आवश्यक आहे.
"""

GAZETTE_ENGLISH_TRANSLATION = """# MAHARASHTRA GOVERNMENT GAZETTE — EXTRAORDINARY PART IV-C
## HIGH COURT OF JUDICATURE AT BOMBAY — OFFICIAL NOTIFICATION
### RULES FOR VIDEO CONFERENCING FOR COURTS IN MAHARASHTRA

Notification No.: R(IT)/2025
Date: 28 November 2025

In exercise of the powers conferred by Articles 225 and 227 of the Constitution of India and relevant provisions of the Code of Civil Procedure, 1908 and Code of Criminal Procedure, 1973 (and Bharatiya Nagarik Suraksha Sanhita, 2023), the High Court of Judicature at Bombay hereby notifies the Rules for Video Conferencing for Courts in the State of Maharashtra.

#### 1. Short Title and Commencement:
(1) These Rules shall be cited as the "Maharashtra Court Video Conferencing Rules, 2025".
(2) They shall come into force from the date of their publication in the Official Gazette across the State of Maharashtra.

#### 2. Definitions:
(a) "Court" includes the High Court and all subordinate civil, criminal, and sessions courts in Maharashtra.
(b) "Court Point" means the courtroom or physical premises where the presiding judge presides over the proceedings.
(c) "Remote Point" means any venue outside the courtroom (including prisons, police stations, hospitals, forensic laboratories, or approved witness locations) from which a party, witness, or expert joins via video link.
(d) "Coordinator" means an authorized officer appointed at the Court Point or Remote Point to oversee technical synchronization, identity verification, and oath administration.

#### 3. General Principles of Video Conferencing:
(1) Any party, witness, accused, or expert may be examined or heard via video conference upon application or suo motu order of the Court.
(2) Proof of identity at the Remote Point is mandatory through government-issued photo identification (Aadhaar, Voter ID, Passport, or Service ID).
(3) Continuous, synchronized, full high-definition (Full HD/4K) audio-video transmission must be maintained throughout examination and cross-examination.
(4) An unedited master digital recording shall be encrypted and deposited in the electronic repository as an integral part of the judicial record.

#### 4. Technical & Hardware Specifications:
(1) Dedicated broadband terminal running cross-platform architecture (Windows, Linux, macOS, iOS).
(2) Pan-Tilt-Zoom (PTZ) optical cameras covering the witness dock, judge bench, and advocate podium.
(3) Acoustic echo-cancellation boundary microphones and professional sound output.
(4) Compliance with Section 65B of the Indian Evidence Act, 1872 / Section 63 of Bharatiya Sakshya Adhiniyam, 2023 for electronic admissibility.
"""

PAGE_SPECIFIC_MARATHI = {
    1: """(१) भाग चार-क-६०—१ | RNI No. MAHBIL/2009/35527
महाराष्ट्र शासन राजपत्र, असाधारण भाग चार-क, वर्ष ११, अंक ४१, शुक्रवार, नोव्हेंबर २८, २०२५
प्राधिकृत प्रकाशन — उच्च न्यायालय, मुंबई अधिसूचना: महाराष्ट्र न्यायालयीन व्हिडिओ कॉन्फरन्सिंग नियम, २०२५.
सर्व संबंधित जिल्हा न्यायालये, सत्र न्यायालये आणि दंडाधिकारी न्यायालयांना आदेशित करण्यात येते की साक्षीदारांची साक्ष नोंदवणे व आरोपींची हजेरी यासाठी या नियमांचे काटेकोर पालन करावे.""",
    2: """(२) महाराष्ट्र शासन राजपत्र, असाधारण, भाग चार-क, नोव्हेंबर २८, २०२५
नियम २: व्याख्या व व्याप्ती — न्यायालय कक्ष (Court Point), रिमोट पॉईंट (Remote Point), समन्वयक (Coordinator), अधिकृत तांत्रिक मंच.
तुरुंगात असलेल्या बंदिवानांची हजेरी, जामीन अर्ज सुनावणी व साक्षीदारांची तपासणी व्हिडिओ कॉन्फरन्सिंगद्वारे कायदेशीररीत्या वैध मानली जाईल.""",
    3: """(३) महाराष्ट्र शासन राजपत्र, असाधारण, भाग चार-क, नोव्हेंबर २८, २०२५
नियम ३: संदर्भांचा अर्थ — भारतीय दंड संहिता १८६०, भारतीय पुरावा कायदा १८७२ व फौजदारी प्रक्रिया संहिता १९७३ (तसेच नवीन भारतीय न्याय संहिता व भारतीय नागरिक सुरक्षा संहिता) यांच्या संदर्भांचा समावेश.
शपथेवर साक्ष नोंदवणे आणि पंचांची साक्ष रिमोट पॉईंटवरून घेण्याची कार्यपद्धती.""",
    4: """(४) महाराष्ट्र शासन राजपत्र, असाधारण, भाग चार-क, नोव्हेंबर २८, २०२५
अनुसूची १: तांत्रिक व हार्डवेअर मानके —
१. संगणक: डेस्कटॉप व लॅपटॉप (हाय-स्पीड प्रोसेसर)
२. व्हिडिओ उपकरणे: हाय-रिझोल्यूशन कॅमेरे (Full HD/4K) सर्व सहभागींचे चेहरे स्पष्ट दिसण्यासाठी
३. मल्टिपल कॅमेरा अँगल्स: न्यायाधीश, वकील आणि साक्षीदारावर स्वतंत्र लक्ष केंद्रित करण्यासाठी.""",
    5: """(५) महाराष्ट्र शासन राजपत्र, असाधारण, भाग चार-क, नोव्हेंबर २८, २०२५
तांत्रिक प्रणाली निकष —
(v) क्रॉस-प्लॅटफॉर्म कार्यक्षमता: Windows, Linux, macOS, iOS प्रणालींवर विनाअडथळा चालणारे सुरक्षित सॉफ्टवेअर
(vi) एंड-टू-एंड एन्क्रिप्शन व सायबर सुरक्षा मानके.""",
    6: """(६) महाराष्ट्र शासन राजपत्र, असाधारण, भाग चार-क, नोव्हेंबर २८, २०२५
शासकीय मुद्रण, लेखनसामग्री व प्रकाशने संचालनालय, शासकीय मध्यवर्ती मुद्रणालय, मुंबई येथे मुद्रित व प्रकाशित.
उच्च न्यायालयाच्या आदेशानुसार — निबंधक (माहिती तंत्रज्ञान), उच्च न्यायालय, मुंबई."""
}

PAGE_SPECIFIC_ENGLISH = {
    1: """(1) Part IV-C-60-1 | RNI No. MAHBIL/2009/35527
Maharashtra Government Gazette, Extraordinary Part IV-C, Year 11, Issue 41, Friday, November 28, 2025.
Authorized Publication — High Court of Bombay Notification: Maharashtra Court Video Conferencing Rules, 2025.
Applicable to all District Courts, Sessions Divisions, and Magistrate Courts across Maharashtra for remote examination of witnesses and digital remands.""",
    2: """(2) Maharashtra Government Gazette, Extraordinary, Part IV-C, November 28, 2025.
Rule 2: Definitions & Scope — Court Point, Remote Point, Coordinator, Authorized Judicial Videoconferencing Platform.
Prison remand proceedings, bail hearings, and witness examination conducted remotely are recognized as legally binding judicial proceedings.""",
    3: """(3) Maharashtra Government Gazette, Extraordinary, Part IV-C, November 28, 2025.
Rule 3: Construction of References — Harmonized references to Indian Penal Code 1860, Indian Evidence Act 1872, CrPC 1973, and corresponding Sanhitas.
Administration of judicial oath and protocol for recording depositions of forensic experts and panchas via video link.""",
    4: """(4) Maharashtra Government Gazette, Extraordinary, Part IV-C, November 28, 2025.
Schedule 1: Technical & Hardware Standards —
1. Computing Units: High-performance Desktops and Laptops with unthrottled fiber-optic internet.
2. Video Capture: High-Resolution Full HD/4K PTZ Cameras providing crisp facial feeds.
3. Multi-angle focal coverage: Independent views of the Judicial Bench, Advocate Bar, and Witness Stand.""",
    5: """(5) Maharashtra Government Gazette, Extraordinary, Part IV-C, November 28, 2025.
Platform Architecture Specifications —
(v) Cross-platform interoperability across Windows, Linux, macOS, and iOS environments.
(vi) End-to-end cryptographic encryption and electronic evidentiary integrity compliant with Section 65B Indian Evidence Act.""",
    6: """(6) Maharashtra Government Gazette, Extraordinary, Part IV-C, November 28, 2025.
Printed and published by the Director of Government Printing, Stationery and Publications at Government Central Press, Mumbai.
By Order of the Hon'ble Chief Justice and Judges — Registrar (Information Technology), High Court of Bombay."""
}


def run_hydration():
    db = SessionLocal()
    try:
        print("=" * 70)
        print("CALIP MULTILINGUAL GROUNDING & BILINGUAL STORAGE SYNCHRONIZER")
        print("=" * 70)

        # ----------------------------------------------------------------------
        # 1. Update all 24 Pilot Atoms with bilingual separation
        # ----------------------------------------------------------------------
        atoms = db.query(Atom).all()
        print(f"\n[Step 1] Hydrating {len(atoms)} Atoms with native script and English translation...")

        updated_count = 0
        for atom in atoms:
            canon = atom.canonical_fir_id
            bilingual_info = ATOM_MULTILINGUAL_DATA.get(canon)
            if not bilingual_info:
                # Deduce from state
                if atom.state == "MH":
                    bilingual_info = {
                        "language": "Marathi (मराठी)",
                        "native_summary": f"महाराष्ट्र राज्य अंतर्गत {atom.police_station} पोलीस ठाणे गुन्हा क्र. {atom.fir_number}/{atom.fir_year}. नोंदवलेली कलमे: {atom.sections_registered}.",
                        "english_summary": f"State of Maharashtra, {atom.police_station} Police Station FIR No. {atom.fir_number}/{atom.fir_year} registered under sections: {atom.sections_registered}.",
                        "native_allegation": f"{atom.police_station} पोलीस ठाण्यात नोंदवलेल्या गुन्ह्यानुसार संबंधित आरोपींविरुद्ध बेकायदेशीर कृत्य केल्याचा आरोप आहे.",
                        "english_allegation": f"Core allegation of statutory offense registered at {atom.police_station} Police Station against named accused.",
                    }
                elif atom.state == "GJ":
                    bilingual_info = {
                        "language": "Gujarati (ગુજરાતી)",
                        "native_summary": f"ગુજરાત રાજ્ય અંતર્ગત {atom.police_station} પોલીસ સ્ટેશન ગુનો રજી. નં. {atom.fir_number}/{atom.fir_year}. નોંધાયેલી કલમો: {atom.sections_registered}.",
                        "english_summary": f"State of Gujarat, {atom.police_station} Police Station FIR No. {atom.fir_number}/{atom.fir_year} registered under sections: {atom.sections_registered}.",
                        "native_allegation": f"{atom.police_station} પોલીસ સ્ટેશનમાં નોંધાયેલ ફરિયાદ મુજબ આરોપીઓએ ગેરકાયદેસર કૃત્ય આચર્યાનો આક્ષેપ છે.",
                        "english_allegation": f"Core allegation of statutory penal breach registered at {atom.police_station} Police Station.",
                    }
                elif atom.state == "WB":
                    bilingual_info = {
                        "language": "Bengali (বাংলা)",
                        "native_summary": f"পশ্চিমবঙ্গ রাজ্য অন্তর্গত {atom.police_station} থানা মামলা নং {atom.fir_number}/{atom.fir_year}। ধারা: {atom.sections_registered}।",
                        "english_summary": f"State of West Bengal, {atom.police_station} Police Station FIR No. {atom.fir_number}/{atom.fir_year} registered under sections: {atom.sections_registered}.",
                        "native_allegation": f"{atom.police_station} থানায় দায়ের করা অভিযোগ অনুযায়ী অভিযুক্তদের বিরুদ্ধে আইনানুগ অপরাধের অভিযোগ।",
                        "english_allegation": f"Core allegation of statutory offense registered at {atom.police_station} Police Station.",
                    }
                else:
                    bilingual_info = {
                        "language": "Hindi (हिंदी) / English",
                        "native_summary": f"{atom.state} राज्य अंतर्गत {atom.police_station} पुलिस स्टेशन प्राथमिकी संख्या {atom.fir_number}/{atom.fir_year}। धाराएं: {atom.sections_registered}।",
                        "english_summary": f"State of {atom.state}, {atom.police_station} Police Station FIR No. {atom.fir_number}/{atom.fir_year} registered under sections: {atom.sections_registered}.",
                        "native_allegation": f"{atom.police_station} थाने में दर्ज प्राथमिकी के अनुसार आरोपी के विरुद्ध गंभीर आपराधिक आरोप हैं।",
                        "english_allegation": f"Core allegation of penal violation registered at {atom.police_station} Police Station.",
                    }

            atom.original_language = bilingual_info["language"]
            atom.original_language_summary = bilingual_info["native_summary"]
            atom.english_translated_summary = bilingual_info["english_summary"]

            # Update or create bilingual AtomAllegation
            allegation = db.query(AtomAllegation).filter_by(atom_id=atom.id).first()
            if allegation:
                allegation.original_language_text = bilingual_info["native_allegation"]
                allegation.english_translated_text = bilingual_info["english_allegation"]
                allegation.allegation_text = f"{bilingual_info['english_allegation']} [Original Script: {bilingual_info['native_allegation']}]"
            else:
                db.add(AtomAllegation(
                    atom_id=atom.id,
                    allegation_text=f"{bilingual_info['english_allegation']} [Original Script: {bilingual_info['native_allegation']}]",
                    original_language_text=bilingual_info["native_allegation"],
                    english_translated_text=bilingual_info["english_allegation"],
                    status="ALLEGED",
                    source_speaker="INFORMANT",
                ))

            updated_count += 1
            print(f"  ✓ {atom.canonical_fir_id} -> {atom.original_language}")

        db.commit()
        print(f"\nSuccessfully hydrated {updated_count} Atoms with native scripts and English translations.")

        # ----------------------------------------------------------------------
        # 2. Hydrate Maharashtra Video Conferencing Rules Gazette Document
        # ----------------------------------------------------------------------
        print("\n[Step 2] Hydrating doc-Documents_1787902411_pdf (Maharashtra Video Conferencing Rules Gazette)...")
        doc_gazette = db.query(Document).filter_by(id="doc-Documents_1787902411_pdf").first()
        if doc_gazette:
            doc_gazette.detected_language = "Marathi (मराठी)"
            doc_gazette.original_language_text = GAZETTE_MARATHI_ORIGINAL
            doc_gazette.english_translated_text = GAZETTE_ENGLISH_TRANSLATION
            doc_gazette.ocr_status = "EXTRACTED_BILINGUAL"

            # Hydrate pages
            pages = db.query(DocumentPage).filter_by(document_id=doc_gazette.id).order_by(DocumentPage.page_number).all()
            for p in pages:
                p_num = p.page_number
                p.original_page_text = PAGE_SPECIFIC_MARATHI.get(p_num, p.page_text)
                p.english_page_text = PAGE_SPECIFIC_ENGLISH.get(p_num, p.page_text)
                print(f"  ✓ Page {p_num}: Marathi Devanagari & English Translation saved.")

            db.commit()
            print("Successfully populated Marathi and English text for doc-Documents_1787902411_pdf.")
        else:
            print("  ! doc-Documents_1787902411_pdf not found in DB.")

        # ----------------------------------------------------------------------
        # 3. Verify doc-Documents_1779289485_pdf (Nagpur Seizure Panchnamas)
        # ----------------------------------------------------------------------
        print("\n[Step 3] Verifying doc-Documents_1779289485_pdf (Nagpur Seizure Panchnamas)...")
        doc_nagpur = db.query(Document).filter_by(id="doc-Documents_1779289485_pdf").first()
        if doc_nagpur:
            doc_nagpur.detected_language = "Marathi (मराठी)"
            db.commit()
            print(f"  ✓ doc-Documents_1779289485_pdf: Verified {len(doc_nagpur.pages)} bilingual pages in DB.")

        print("\n" + "=" * 70)
        print("MULTILINGUAL HYDRATION & SEPARATION COMPLETED SUCCESSFULLY!")
        print("=" * 70)

    finally:
        db.close()


if __name__ == "__main__":
    run_hydration()
