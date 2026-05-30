# ==========================================
# TRANSLATION & LOCALIZATION ENGINE DATA
# ==========================================

LANG_DICT = {
    "en": {
        "title": "🍔 MapBite Market Intelligence Dashboard",
        "subtitle": "Benchmark your location, map competitor density, and evaluate neighborhood market power.",
        "sidebar_settings": "📍 Target Setup",
        "lang_lbl": "🌐 Language / Γλώσσα",
        "categories_title": "Target Categories:",
        "categories_opt": {
            "Restaurants 🍔": "restaurant",
            "Cafes ☕": "cafe",
            "Bakeries & Pastry 🥐": "bakery",  # Clear and accurate
            "Bars & Pubs 🍺": "bar",
            "Takeaway / Fast Food 🍕": "fast_food_restaurant"
        },
        "keyword_lbl": "Keyword Sub-Filter:",
        "keyword_ph": "e.g., Italian, Sushi, Specialty Coffee, Pizza",
        "keyword_help": "Narrow down selected categories to a specific style query.",
        "loc_mode_lbl": "Location Selection Mode:",
        "loc_mode_opt": ["🔍 Type an Address / Landmark", "⌨️ Input Coordinates Directly"],
        "addr_lbl": "Enter Target Location Address:",
        "addr_ph": "e.g., Syntagma Square, Athens",
        "addr_success": "🎯 Target Locked:",
        "addr_error": "❌ Could not resolve address. Try verifying the spelling!",
        "addr_info": "💡 Type an address or click anywhere on the map grid layout.",
        "coord_lbl": "Target Coordinates (Lat, Lng):",
        "coord_help": "Pasting coordinates or clicking the map will overwrite this text block instantly.",
        "coord_error": "Format error. Please use: latitude, longitude",
        "radius_lbl": "Search Scan Radius (Meters)",
        "btn_run": "🚀 Run Competitive Analysis",
        "btn_spinner": "Analyzing neighborhood market dynamics...",
        "no_results": "📭 No active listings matched your specific category + keyword criteria in this area.",
        "resource_lbl": "### 📊 App Resource Monitor",
        "limit_lbl": "Daily Limit Usage:",
        "limit_reached": "🚨 System Daily Query Limit Reached! Try again tomorrow.",
        "metric_panel_lbl": "### 📊 Dual-Score Metric Matrix",
        "metric_panel_text": """
**🔴 Opportunity Score (Quality Gap)**
* Measures high-volume areas with low customer satisfaction scores. Focuses entirely on raw market operational vulnerabilities.

**💰 Premium Gap Score (Value Deficit)**
* Multiplies the core opportunity index against price tiers. Flags expensive venues charging premium prices but failing to deliver quality.
""",
        "lens_lbl": "### 🛠️ Intelligence Lens Selector",
        "lens_choices": ["🔴 Find Market Gaps & Vulnerabilities (Worst Rated/Highest Traffic)", 
                        "👑 Study Market Leaders & Dominance (Best Rated/Highest Traffic)"],
        "peak_opp_lbl": "Peak Opportunity Score",
        "peak_opp_delta": "High Market Gap",
        "peak_dom_lbl": "Peak Dominance Score",
        "peak_dom_delta": "Market Leader to Beat",
        "map_init_info": "💡 Map initialization active. Click anywhere on the map or type an address in the sidebar, then run the analysis to view comparative data matrix frames.",
        "map_title": "🗺️ Strategic Analysis Map",
        "map_epicenter_pop": "📍 <b>Your Proposed Site Core</b>",
        "map_epicenter_tt": "Search Epicenter (Click Map to Move Here)",
        "map_popup_status": "Status",
        "map_popup_rating": "Current Rating:",
        "map_popup_reviews": "Review Count:",
        "map_popup_opp_idx": "Opportunity Index:",
        "map_popup_dom_idx": "Dominance Index:",
        "legend_title": "### 📋 Dashboard Map & Operating Schedule Legend Matrix",
        "leg1_gap": "<strong>🟣 Rank #1: Top Opportunity</strong><br><small>Peak engagement volume combined with lower satisfaction ratings.</small>",
        "leg2_gap": "<strong>🔵 Ranks #2-4: Strong Entry</strong><br><small>High consumer traffic footprints showing clear competitive performance gaps.</small>",
        "leg3_gap": "<strong>🟢 Ranks #5-8: Viable Gap</strong><br><small>Moderate traffic areas with room for strategic market entry optimization.</small>",
        "leg1_dom": "<strong>👑 Rank #1: Market Leader</strong><br><small>Apex territory competitor. Commanding volume with elite reputation management.</small>",
        "leg2_dom": "<strong>🔸 Ranks #2-4: Premium Tier</strong><br><small>Dependable high-traction establishments maintaining top tier market volume.</small>",
        "leg3_dom": "<strong>🟤 Ranks #5-8: Mainstream Core</strong><br><small>Established standard neighborhood options with healthy market presence.</small>",
        "leg_hours": "<strong>⏰ Operational Status Codes</strong><br><small>🟢 <b>Open:</b> Operating right now.<br>🔴 <b>Closed:</b> Closed/Out of hours.<br>⚪ <b>N/A:</b> Google listing lacks hours data.</small>",
        "matrix_title": "📊 Intelligence Analytics Matrix",
        "col_rank": "Rank",
        "col_establishment": "Establishment",
        "col_status": "Operational Status",
        "col_profile": "Strategic Profile",
        "col_rating": "Rating",
        "col_reviews": "Reviews",
        "col_price": "Price Tier",
        "col_gap": "Opportunity Score",
        "col_deficit": "Premium Gap Score",
        "col_dom": "Market Dominance Score",
        "col_menu": "Menu",
        "col_menu_btn": "📋 View Menu",
        "col_site": "Site Link",
        "col_site_btn": "Open 🔗",
        "method_title": "📊 Metric Methodology & Formulas",
        "method_text": """
**1. Opportunity Score (Find Market Gaps)**
* **Formula:** `log(Total Reviews + 1) × (5.0 - Rating)²`
* *Rationale:* Identifies high-traffic establishments (high review count) that are underperforming (low rating). The squared difference heavily penalizes poor ratings, spotlighting immediate market gaps where a better service could easily capture unhappy customers.

**2. Premium Gap Score**
* **Formula:** `Opportunity Score × (Price Level / 2.0)`
* *Rationale:* Highlights places that charge a premium (higher price tiers) but deliver poor quality. An overpriced, low-rated competitor represents a massive vulnerability and a prime target for disruption.

**3. Market Dominance Score (Market Leader Profile)**
* **Formula:** `log(Total Reviews + 1) × Rating`
* *Rationale:* Combines volume (popularity) with quality (rating). High scores indicate entrenched market leaders with a strong reputation and massive foot traffic.
"""
    },
    "el": {
        "title": "🍔 MapBite Dashboard Εμπορικής Ευφυΐας",
        "subtitle": "Αξιολογήστε την τοποθεσία σας, χαρτογραφήστε τον ανταγωνισμό και αναλύστε την ισχύ της τοπικής αγοράς.",
        "sidebar_settings": "📍 Ρυθμίσεις Τοποθεσίας",
        "lang_lbl": "🌐 Γλώσσα / Language",
        "categories_title": "Κατηγορίες Στόχοι:",
        "categories_opt": {
            "Εστιατόρια 🍔": "restaurant",
            "Καφετέριες ☕": "cafe",
            "Φούρνοι 🥐": "bakery",
            "Μπαρ & Παμπ 🍺": "bar",
            "Fast Food / Takeaway 🍕": "fast_food_restaurant"
        },
        "keyword_lbl": "Φίλτρο Λέξεων-Κλειδιών:",
        "keyword_ph": "π.χ., Ιταλικό, Σούσι, Specialty καφές, Πίτσα",
        "keyword_help": "Περιορίστε τις επιλεγμένες κατηγορίες σε ένα συγκεκριμένο στυλ κουζίνας.",
        "loc_mode_lbl": "Μέθοδος Επιλογής Τοποθεσίας:",
        "loc_mode_opt": ["🔍 Πληκτρολόγηση Διεύθυνσης / Σημείου", "⌨️ Απευθείας Εισαγωγή Συντεταγμένων"],
        "addr_lbl": "Εισάγετε Διεύθυνση Τοποθεσίας Στόχου:",
        "addr_ph": "π.χ., Πλατεία Συντάγματος, Αθήνα",
        "addr_success": "🎯 Στόχος Κλείδωσε:",
        "addr_error": "❌ Αδυναμία εύρεσης διεύθυνσης. Ελέγξτε την ορθογραφία!",
        "addr_info": "💡 Πληκτρολογήστε μια διεύθυνση ή κάντε κλικ οπουδήποτε στον χάρτη.",
        "coord_lbl": "Συντεταγμένες Στόχου (Lat, Lng):",
        "coord_help": "Η επικόλληση συντεταγμένων ή το κλικ στον χάρτη θα αντικαταστήσει αυτό το πεδίο αμέσως.",
        "coord_error": "Σφάλμα μορφής. Παρακαλώ χρησιμοποιήστε: γεωγραφικό πλάτος, γεωγραφικό μήκος",
        "radius_lbl": "Ακτίνα Σάρωσης (Μέτρα)",
        "btn_run": "🚀 Έναρξη Ανάλυσης Ανταγωνισμού",
        "btn_spinner": "Ανάλυση δυναμικής της τοπικής αγοράς...",
        "no_results": "📭 Δεν βρέθηκαν επιχειρήσεις που να ταιριάζουν με την κατηγορία και τα κριτήριά σας σε αυτή την περιοχή.",
        "resource_lbl": "### 📊 Παρακολούθηση Πόρων",
        "limit_lbl": "Ημερήσια Χρήση Ορίου:",
        "limit_reached": "🚨 Εξαντλήθηκε το Ημερήσιο Όριο Ερωτημάτων! Δοκιμάστε ξανά αύριο.",
        "metric_panel_lbl": "### 📊 Μήτρα Διπλής Βαθμολογίας",
        "metric_panel_text": """
**🔴 Δείκτης Ποιοτικού Κενού (Opportunity Score)**
* Μετρά περιοχές με υψηλό όγκο κίνησης αλλά χαμηλή βαθμολογία ικανοποίησης πελατών. Εστιάζει στις λειτουργικές αδυναμίες της αγοράς.

**💰 Δείκτης Ελλείμματος Αξίας (Premium Gap Score)**
* Πολλαπλασιάζει τον βασικό δείκτη ευκαιρίας με τις κατηγορίες τιμών. Επισημαίνει ακριβά καταστήματα που αποτυγχάνουν να προσφέρουν ποιότητα ανάλογη της τιμής τους.
""",
        "lens_lbl": "### 🛠️ Επιλογέας Φακού Ανάλυσης",
        "lens_choices": ["🔴 Εύρεση Κενών Αγοράς & Αδυναμιών (Χαμηλότερη Βαθμολογία/Υψηλή Κίνηση)", 
                        "👑 Μελέτη Ηγετών Αγοράς & Κυριαρχίας (Υψηλότερη Βαθμολογία/Υψηλή Κίνηση)"],
        "peak_opp_lbl": "Μέγιστος Δείκτης Ευκαιρίας",
        "peak_opp_delta": "Μεγάλο Κενό Αγοράς",
        "peak_dom_lbl": "Μέγιστος Δείκτης Κυριαρχίας",
        "peak_dom_delta": "Ηγέτης Αγοράς προς Αντιμετώπιση",
        "map_init_info": "💡 Ο χάρτης είναι ενεργός. Κάντε κλικ οπουδήποτε στον χάρτη ή πληκτρολογήστε μια διεύθυνση, και πατήστε έναρξη ανάλυσης.",
        "map_title": "🗺️ Χάρτης Στρατηγικής Ανάλυσης",
        "map_epicenter_pop": "📍 <b>Προτεινόμενο Σημείο Καταστήματος</b>",
        "map_epicenter_tt": "Επίκεντρο Αναζήτησης (Κάντε κλικ στον χάρτη για μετακίνηση)",
        "map_popup_status": "Κατάσταση",
        "map_popup_rating": "Τρέχουσα Βαθμολογία:",
        "map_popup_reviews": "Σύνολο Κριτικών:",
        "map_popup_opp_idx": "Δείκτης Ευκαιρίας:",
        "map_popup_dom_idx": "Δείκτης Κυριαρχίας:",
        "legend_title": "### 📋 Υπόμνημα Χάρτη & Μήτρας Λειτουργίας",
        "leg1_gap": "<strong>🟣 Κατάταξη #1: Κορυφαία Ευκαιρία</strong><br><small>Υψηλός όγκος αλληλεπίδρασης σε συνδυασμό με χαμηλές βαθμολογίες ικανοποίησης.</small>",
        "leg2_gap": "<strong>🔵 Κατάταξη #2-4: Ισχυρή Είσοδος</strong><br><small>Μεγάλο αποτύπωμα επισκεψιμότητας με εμφανή competitive performance κενά.</small>",
        "leg3_gap": "<strong>🟢 Κατάταξη #5-8: Βιώσιμο Κενό</strong><br><small>Περιοχές μέσης κίνησης με περιθώρια στρατηγικής βελτιστοποίησης.</small>",
        "leg1_dom": "<strong>👑 Κατάταξη #1: Ηγέτης Αγοράς</strong><br><small>Κορυφαίος ανταγωνιστής περιοχής. Κυρίαρχος όγκος με άριστη διαχείριση φήμης.</small>",
        "leg2_dom": "<strong>🔸 Κατάταξη #2-4: Premium Κατηγορία</strong><br><small>Σταθερές επιχειρήσεις υψηλής απήχησης που διατηρούν κορυφαίο όγκο αγοράς.</small>",
        "leg3_dom": "<strong>🟤 Κατάταξη #5-8: Κεντρικός Πυρήνας</strong><br><small>Καθιερωμένες τυπικές επιλογές της γειτονιάς με υγιή παρουσία στην αγορά.</small>",
        "leg_hours": "<strong>⏰ Κωδικοί Κατάστασης Λειτουργίας</strong><br><small>🟢 <b>Ανοιχτό:</b> Λειτουργεί αυτή τη στιγμή.<br>🔴 <b>Κλειστό:</b> Εκτός ωραρίου λειτουργίας.<br>⚪ <b>N/A:</b> Δεν υπάρχουν δεδομένα ωραρίου στη Google.</small>",
        "matrix_title": "📊 Πίνακας Αναλυτικής Ευφυΐας",
        "col_rank": "Κατάταξη",
        "col_establishment": "Κατάστημα",
        "col_status": "Κατάσταση Λειτουργίας",
        "col_profile": "Στρατηγικό Προφίλ",
        "col_rating": "Βαθμολογία",
        "col_reviews": "Κριτικές",
        "col_price": "Κατηγορία Τιμής",
        "col_gap": "Δείκτης Ευκαιρίας",
        "col_deficit": "Δείκτης Υπερτιμολόγησης",
        "col_dom": "Δείκτης Κυριαρχίας Αγοράς",
        "col_menu": "Μενού",
        "col_menu_btn": "📋 Προβολή Μενού",
        "col_site": "Σύνδεσμος",
        "col_site_btn": "Άνοιγμα 🔗",
        "method_title": "📊 Μεθοδολογία & Τύποι Υπολογισμού",
        "method_text": """
**1. Δείκτης Ευκαιρίας (Εύρεση Κενών)**
* **Τύπος:** `log(Σύνολο Κριτικών + 1) × (5.0 - Βαθμολογία)²`
* *Λογική:* Εντοπίζει καταστήματα με υψηλή επισκεψιμότητα (πολλές κριτικές) αλλά κακή απόδοση (χαμηλή βαθμολογία). Το τετράγωνο της διαφοράς τιμωρεί αυστηρά τις κακές βαθμολογίες, αναδεικνύοντας άμεσα κενά στην αγορά όπου καλύτερες υπηρεσίες θα μπορούσαν να κερδίσουν δυσαρεστημένους πελάτες.

**2. Δείκτης Υπερτιμολόγησης (Premium Gap)**
* **Τύπος:** `Δείκτης Ευκαιρίας × (Επίπεδο Τιμής / 2.0)`
* *Λογική:* Αναδεικνύει μέρη που χρεώνουν ακριβά (υψηλότερα επίπεδα τιμών) αλλά προσφέρουν κακή ποιότητα. Ένας ακριβός ανταγωνιστής με χαμηλή βαθμολογία αποτελεί ιδανικό στόχο για ανταγωνιστική είσοδο.

**3. Δείκτης Κυριαρχίας Αγοράς (Προφίλ Ηγέτη)**
* **Τύπος:** `log(Σύνολο Κριτικών + 1) × Βαθμολογία`
* *Λογική:* Συνδυάζει τον όγκο (δημοτικότητα) με την ποιότητα (βαθμολογία). Οι υψηλές βαθμολογίες υποδεικνύουν εδραιωμένους ηγέτες της αγοράς με ισχυρή φήμη.
"""
    }
}