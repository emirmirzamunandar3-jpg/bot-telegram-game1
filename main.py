import os
import random
import asyncio
import logging
from datetime import datetime
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    ApplicationBuilder,
    ContextTypes,
    CommandHandler,
    CallbackQueryHandler,
    ConversationHandler,
    MessageHandler,
    filters
)

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# --- TOKEN DUA BOT LU ---
TOKEN_BOT_1 = '8753900489:AAEjGTHmPLQuXy411u92gonTAU5Wk54gz3k'
TOKEN_BOT_2 = '8767579357:AAHqapyf9AJj7iItE7rA3E3aiw8zSL6J_bo'

# --- STATE CONVERSATION ---
(
    STATE_TEBAK_ANGKA,
    STATE_TEBAK_KATA,
    STATE_CUSTOM_INPUT
) = range(3)

# =====================================================================
# MODUL 1: CORE ENGINE & DATABASE SIMULATOR (EXTENDED LINE EXPANSION)
# =====================================================================
class BotEngineCore:
    def __init__(self, bot_name: str):
        self.bot_name = bot_name
        self.active_sessions = {}
        self.analytics_counter = 0
        logger.info(f"Modul Core Engine diinisialisasi untuk: {self.bot_name}")

    def increment_analytics(self):
        self.analytics_counter += 1
        return self.analytics_counter

    async def purge_old_sessions(self):
        current_time = datetime.now()
        expired_keys = []
        for user_id, data in self.active_sessions.items():
            diff = (current_time - data.get('time', current_time)).seconds
            if diff > 3600:
                expired_keys.append(user_id)
        for key in expired_keys:
            del self.active_sessions[key]


# =====================================================================
# MODUL 2: GAME TEBAK ANGKA MISTIK (ADVANCED LOGIC)
# =====================================================================
async def game_tebak_angka_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    context.user_data['secret_num'] = random.randint(1, 100)
    context.user_data['tries'] = 0
    
    await query.message.edit_text(
        "🔮 **GAME 1: TEBAK ANGKA MISTIK (1-100)**\n\n"
        "Gw udah pegang angka rahasia. Coba tebak berapa angka di kepala gw, Bos!\n"
        "Ketik angka pilihan lu langsung di chat, tolol!\n\n"
        "*(Ketik /cancel buat batal)*",
        parse_mode='Markdown'
    )
    return STATE_TEBAK_ANGKA

async def game_tebak_angka_process(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text
    try:
        tebakan = int(text)
    except ValueError:
        await update.message.reply_text("Waduh, itu bukan angka, tolol! Masukin angka 1 sampe 100:")
        return STATE_TEBAK_ANGKA

    secret = context.user_data.get('secret_num', 50)
    context.user_data['tries'] = context.user_data.get('tries', 0) + 1
    tries = context.user_data['tries']

    if tebakan < secret:
        await update.message.reply_text(f"📉 Tebakan ke-{tries}: **Kecilan, Bos!** Naikkin lagi angkanya, tolol:", parse_mode='Markdown')
        return STATE_TEBAK_ANGKA
    elif tebakan > secret:
        await update.message.reply_text(f"📈 Tebakan ke-{tries}: **Kepala batok lu, ketinggian!** Turunin angkanya, tolol:", parse_mode='Markdown')
        return STATE_TEBAK_ANGKA
    else:
        kb = [[InlineKeyboardButton("« Kembali ke Menu Utama", callback_data="menu_back")]]
        await update.message.reply_text(
            f"🎉 **MANTAP KALI, BISA PAS!** 🎉, tolol\n\n"
            f"Angka rahasianya emang **{secret}**!\n"
            f"Lu berhasil nebak dalam **{tries} kali percobaan**.",
            reply_markup=InlineKeyboardMarkup(kb),
            parse_mode='Markdown'
        )
        return ConversationHandler.END


# =====================================================================
# MODUL 3: KUIS TEBAK MEREK HP & GADGET
# =====================================================================
async def game_tebak_hp_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    
    list_soal = [
        ("Merek HP lipat sejuta umat yang casing belakangnya sering ada varian 'Porsche Design', apa tuh?", "Huawei"),
        ("HP gaming legendaris yang punya kipas RGB internal langsung di dalam bodinya, merek apa?", "RedMagic"),
        ("Pelopor HP kamera boba tiga biji dengan logo buah digigit setengah, merek apa?", "Apple"),
        ("Merek asal China yang terkenal dengan sub-brand 'POCO' dan 'Redmi', apa tuh?", "Xiaomi"),
        ("Merek HP asal Korea Selatan yang punya seri flagship 'Galaxy S' dan 'Galaxy Z', apa tuh?", "Samsung"),
        ("Merek HP yang terkenal dengan seri 'ROG Phone' khusus buat gaming hardcore, apa tuh?", "Asus")
    ]
    soal, jawaban = random.choice(list_soal)
    
    keyboard = [
        [InlineKeyboardButton("💡 Bocorin Jawabannya", callback_data=f"hp_jawab_{jawaban}")],
        [InlineKeyboardButton("🔄 Ganti Soal Lain", callback_data="game_tebak_hp")],
        [InlineKeyboardButton("« Kembali ke Menu", callback_data="menu_back")]
    ]
    
    await query.message.edit_text(
        f"📱 **GAME 2: KUIS TEBAK MEREK HP**\n\n"
        f"❓ **Pertanyaan:**\n_{soal}_\n\n"
        "Kira-kira merek HP apa nih, Bos?",
        reply_markup=InlineKeyboardMarkup(keyboard),
        parse_mode='Markdown'
    )

async def game_tebak_hp_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    data = query.data
    
    if data.startswith("hp_jawab_"):
        kunci = data.replace("hp_jawab_", "")
        kb = [
            [InlineKeyboardButton("📱 Main Kuis HP Lagi", callback_data="game_tebak_hp")],
            [InlineKeyboardButton("« Kembali ke Menu", callback_data="menu_back")]
        ]
        await query.message.edit_text(
            f"✅ Jawabannya yang bener adalah: **{kunci}**!\nGampang banget kan, tolol?",
            reply_markup=InlineKeyboardMarkup(kb),
            parse_mode='Markdown'
        )


# =====================================================================
# MODUL 4: BATU KERTAS GUNTING (SUWEN)
# =====================================================================
async def game_bkg_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    
    keyboard = [
        [
            InlineKeyboardButton("✊ Batu", callback_data="bkg_batu"),
            InlineKeyboardButton("🖐️️ Kertas", callback_data="bkg_kertas"),
            InlineKeyboardButton("✌️ Gunting", callback_data="bkg_gunting")
        ],
        [InlineKeyboardButton("« Kembali ke Menu", callback_data="menu_back")]
    ]
    await query.message.edit_text(
        "✊🖐️✌️ **GAME 3: DUEL BATU KERTAS GUNTING**\n\n"
        "Pilih salah satu senjata lu di bawah buat ngelawan bot, tolol!",
        reply_markup=InlineKeyboardMarkup(keyboard),
        parse_mode='Markdown'
    )

async def game_bkg_play(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    choice = query.data.replace("bkg_", "")
    
    choices_map = {"batu": "✊ Batu", "kertas": "🖐️ Kertas", "gunting": "✌️ Gunting"}
    bot_choice_key = random.choice(["batu", "kertas", "gunting"])
    bot_choice = choices_map[bot_choice_key]
    user_choice = choices_map[choice]
    
    if choice == bot_choice_key:
        hasil = "🤝 **SERI!** Gak ada yang mau ngalah, tolol!"
    elif (
        (choice == "batu" and bot_choice_key == "gunting") or
        (choice == "kertas" and bot_choice_key == "batu") or
        (choice == "gunting" and bot_choice_key == "kertas")
    ):
        hasil = "🏆 **LU MENANG, BOS!** Hoki lu lagi bagus, tolol!"
    else:
        hasil = "💀 **LU KALAH, BOS!** Makanya jangan sok jago, tolol!"

    kb = [
        [InlineKeyboardButton("🔄 Main Suwen Lagi", callback_data="game_bkg")],
        [InlineKeyboardButton("« Kembali ke Menu", callback_data="menu_back")]
    ]
    
    await query.message.edit_text(
        f"✊🖐️✌ **HASIL DUEL SUWEN**\n\n"
        f"• Pilihan Lu: {user_choice}\n"
        f"• Pilihan Bot: {bot_choice}\n\n"
        f"{hasil}",
        reply_markup=InlineKeyboardMarkup(kb),
        parse_mode='Markdown'
    )


# =====================================================================
# MODUL 5: GENERATOR PROMPT GAMBAR AI
# =====================================================================
async def generator_gambar_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    
    list_prompt = [
        "Cyberpunk Jakarta street at night, neon lights, flying motor bebek, wet asphalt reflection, cinematic lighting, 8k resolution.",
        "A cool cat wearing a gangster jacket in Old Town Jakarta style, holding a coffee cup, detailed fur, digital art style.",
        "Futuristic warrior from Jakarta with traditional batik armor, holding a glowing weapon, epic background, hyperrealistic.",
        "Retro vintage Vespa scooter cruising through Menteng street during golden hour, cinematic film grain, aesthetic."
    ]
    pilihan_prompt = random.choice(list_prompt)
    
    keyboard = [
        [InlineKeyboardButton("🎨 Acak Prompt Lain", callback_data="menu_gambar")],
        [InlineKeyboardButton("« Kembali ke Menu Utama", callback_data="menu_back")]
    ]
    
    await query.message.edit_text(
        f"🎨 **FITUR 4: GENERATOR PROMPT GAMBAR AI**\n\n"
        "Nih contoh prompt teks keren buat lu lempar ke AI pembuat gambar:\n\n"
        f"`{pilihan_prompt}`\n\n"
        "Salin teks di atas, terus generate jadi gambar sesuka lu, tolol!",
        reply_markup=InlineKeyboardMarkup(keyboard),
        parse_mode='Markdown'
    )


# =====================================================================
# MODUL 6: KUIS ASAH OTAK & TEBAKAN KOCAK
# =====================================================================
async def kuis_asah_otak_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    
    list_teka_teki = [
        ("Gajah apa yang belalainya pendek?", "Gajah pesek (mana gw tahu)"),
        ("Kenapa pohon kelapa di depan rumah harus ditebang?", "Kalau dicabut berat, tolol!"),
        ("Hewan apa yang paling hening sedunia?", "Kucing (kucing-an sunyi)"),
        ("Ayam apa yang bisa bikin kita masuk angin?", "Ayam kerokan!")
    ]
    tanya, jawab = random.choice(list_teka_teki)
    
    keyboard = [
        [InlineKeyboardButton("💡 Buka Jawabannya", callback_data=f"teka_jawab_{jawab}")],
        [InlineKeyboardButton("🔄 Pertanyaan Lain", callback_data="menu_asah_otak")],
        [InlineKeyboardButton("« Kembali ke Menu", callback_data="menu_back")]
    ]
    
    await query.message.edit_text(
        f"🧠 **FITUR 5: ASAH OTAK & TEBAKAN KOCAK**\n\n"
        f"❓ **Teka-teki:**\n_{tanya}_\n\n"
        "Coba jawab di kepala lu, terus pencet tombol di bawah buat nyocokin, tolol!",
        reply_markup=InlineKeyboardMarkup(keyboard),
        parse_mode='Markdown'
    )

async def kuis_asah_otak_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    data = query.data
    
    if data.startswith("teka_jawab_"):
        kunci = data.replace("teka_jawab_", "")
        kb = [
            [InlineKeyboardButton("🧠 Teka-teki Lagi", callback_data="menu_asah_otak")],
            [InlineKeyboardButton("« Kembali ke Menu", callback_data="menu_back")]
        ]
        await query.message.edit_text(
            f"✅ Jawabannya:\n**{kunci}**\n\nNgakak kan lu, tolol?",
            reply_markup=InlineKeyboardMarkup(kb),
            parse_mode='Markdown'
        )


# =====================================================================
# MODUL 7: KUIS TEBAK TOKOH SEJARAH
# =====================================================================
async def game_tokoh_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    
    list_tokoh = [
        ("Ilmuwan jenius pencetus Teori Relativitas (E=mc²) yang rambutnya berantakan, siapa dia?", "Albert Einstein"),
        ("Penemu bola lampu pijar komersial yang penemuannya menerangi dunia, siapa dia?", "Thomas Alva Edison"),
        ("Bapak Proklamator kemerdekaan Republik Indonesia sekaligus Presiden pertama RI, siapa beliau?", "Ir. Soekarno"),
        ("Penemu mesin uap yang jadi tonggak awal Revolusi Industri, siapa dia?", "James Watt")
    ]
    tanya_tokoh, jawab_tokoh = random.choice(list_tokoh)
    
    keyboard = [
        [InlineKeyboardButton("💡 Lihat Nama Tokoh", callback_data=f"tokoh_jawab_{jawab_tokoh}")],
        [InlineKeyboardButton("🔄 Ganti Tokoh Lain", callback_data="menu_tokoh")],
        [InlineKeyboardButton("« Kembali ke Menu", callback_data="menu_back")]
    ]
    
    await query.message.edit_text(
        f"📜 **GAME 6: KUIS TEBAK TOKOH SEJARAH**\n\n"
        f"❓ **Deskripsi:**\n_{tanya_tokoh}_\n\n"
        "Kira-kira siapa nama tokoh terkenal ini, Bos?",
        reply_markup=InlineKeyboardMarkup(keyboard),
        parse_mode='Markdown'
    )

async def game_tokoh_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    data = query.data
    
    if data.startswith("tokoh_jawab_"):
        kunci = data.replace("tokoh_jawab_", "")
        kb = [
            [InlineKeyboardButton("📜 Tebak Tokoh Lagi", callback_data="menu_tokoh")],
            [InlineKeyboardButton("« Kembali ke Menu", callback_data="menu_back")]
        ]
        await query.message.edit_text(
            f"✅ Tokoh yang dimaksud adalah: **{kunci}**!\nIlmu sejarah lu lumayan juga, tolol!",
            reply_markup=InlineKeyboardMarkup(kb),
            parse_mode='Markdown'
        )


# =====================================================================
# MODUL 8: KAMUS SLANG & SINGKATAN GAUL JAKTIM
# =====================================================================
async def game_gaul_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    
    list_gaul = [
        ("Apa kepanjangan dari singkatan tongkrongan 'mager'?", "Malas gerak"),
        ("Apa arti kata gaul 'mantul' di kamus anak Jaksel/Jaktim?", "Mantap betul"),
        ("Apa kepanjangan dari istilah gaul 'julid'?", "Judes dan pedas / Suka ngomongin orang"),
        ("Apa arti kata 'norak' kalau diledek sama anak tongkrongan?", "Kampungan / gak update pergaulan")
    ]
    tanya_gaul, jawab_gaul = random.choice(list_gaul)
    
    keyboard = [
        [InlineKeyboardButton("💡 Buka Arti Gaul", callback_data=f"gaul_jawab_{jawab_gaul}")],
        [InlineKeyboardButton("🔄 Istilah Lain", callback_data="menu_gaul")],
        [InlineKeyboardButton("« Kembali ke Menu", callback_data="menu_back")]
    ]
    
    await query.message.edit_text(
        f"🗣️ **GAME 7: KAMUS SLANG & SINGKATAN GAUL**\n\n"
        f"❓ **Pertanyaan:**\n_{tanya_gaul}_\n\n"
        "Coba tebak artinya, Bos!",
        reply_markup=InlineKeyboardMarkup(keyboard),
        parse_mode='Markdown'
    )

async def game_gaul_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    data = query.data
    
    if data.startswith("gaul_jawab_"):
        kunci = data.replace("gaul_jawab_", "")
        kb = [
            [InlineKeyboardButton("🗣️ Main Slang Lagi", callback_data="menu_gaul")],
            [InlineKeyboardButton("« Kembali ke Menu", callback_data="menu_back")]
        ]
        await query.message.edit_text(
            f"✅ Artinya yang bener: **{kunci}**!\nAnak jalanan banget lu, tolol!",
            reply_markup=InlineKeyboardMarkup(kb),
            parse_mode='Markdown'
        )


# =====================================================================
# MENU UTAMA UNIVERSAL KEDUA BOT
# =====================================================================
async def start_universal(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [InlineKeyboardButton("🎮 Main Tebak Angka Mistik", callback_data="game_tebak_angka")],
        [InlineKeyboardButton("📱 Kuis Tebak Merek HP", callback_data="game_tebak_hp")],
        [InlineKeyboardButton("✊ Duel Batu Kertas Gunting", callback_data="game_bkg")],
        [InlineKeyboardButton("🧠 Asah Otak & Teka-teki Kocak", callback_data="menu_asah_otak")],
        [InlineKeyboardButton("📜 Kuis Tebak Tokoh Sejarah", callback_data="menu_tokoh")],
        [InlineKeyboardButton("🗣️ Kamus Slang & Singkatan Gaul", callback_data="menu_gaul")],
        [InlineKeyboardButton("🎨 Buat Ide Prompt Gambar AI", callback_data="menu_gambar")],
        [InlineKeyboardButton("⚡ Uji Coba Self-Spam Game", callback_data="self_spam_game")],
        [InlineKeyboardButton("🛑 Hentikan Semua Proses Bot", callback_data="action_stop")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    teks = (
        "🕹️ **PUSAT ARCADE 7 GAME DUA BOT SERENTAK** 🕹️, tolol\n\n"
        "Lu lagi akses bot gabungan pusat game terlengkap. Pilih menu permainan di bawah, Bos!"
    )
    
    if update.callback_query:
        await update.callback_query.message.edit_text(teks, reply_markup=reply_markup, parse_mode='Markdown')
    else:
        await update.message.reply_text(teks, reply_markup=reply_markup, parse_mode='Markdown')


# --- CALLBACK ROUTER UTAMA ---
async def callback_router(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    data = query.data

    if data == "game_tebak_hp":
        await game_tebak_hp_menu(update, context)
    elif data.startswith("hp_jawab_"):
        await game_tebak_hp_callback(update, context)
    elif data == "game_bkg":
        await game_bkg_menu(update, context)
    elif data.startswith("bkg_"):
        await game_bkg_play(update, context)
    elif data == "menu_asah_otak":
        await kuis_asah_otak_menu(update, context)
    elif data.startswith("teka_jawab_"):
        await kuis_asah_otak_callback(update, context)
    elif data == "menu_tokoh":
        await game_tokoh_menu(update, context)
    elif data.startswith("tokoh_jawab_"):
        await game_tokoh_callback(update, context)
    elif data == "menu_gaul":
        await game_gaul_menu(update, context)
    elif data.startswith("gaul_jawab_"):
        await game_gaul_callback(update, context)
    elif data == "menu_gambar":
        await generator_gambar_menu(update, context)
    elif data == "self_spam_game":
        chat_id = query.message.chat_id
        kb = [[InlineKeyboardButton("« Kembali", callback_data="menu_back")]]
        await query.message.edit_text("⚡ **Simulasi Spam Game Dobel Bot Aktif!**", reply_markup=InlineKeyboardMarkup(kb))
        asyncio.create_task(run_self_spam_arcade(context, chat_id))
    elif data == "action_stop":
        context.user_data['stop_spam'] = True
        kb = [[InlineKeyboardButton("« Kembali", callback_data="menu_back")]]
        await query.message.edit_text("🛑 **Semua Proses Alarm / Spam Dihentikan!**", reply_markup=InlineKeyboardMarkup(kb))
    elif data == "menu_back":
        await start_universal(update, context)


async def run_self_spam_arcade(context: ContextTypes.DEFAULT_TYPE, chat_id: int):
    context.user_data['stop_spam'] = False
    count = 0
    while not context.user_data.get('stop_spam', False):
        count += 1
        try:
            await context.bot.send_message(
                chat_id=chat_id,
                text=f"🕹️ **[TEST ARCADE DOBEL BOT #{count}]**\nSistem game dobel bot jalan mulus tanpa ngadat, tolol!",
                parse_mode='Markdown'
            )
        except:
            pass
        await asyncio.sleep(0.6)


async def cancel_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("❌ Permainan dibatalkan, tolol!")
    return ConversationHandler.END


# =====================================================================
# FUNGSI RUNNER UTAMA (DIPERBAIKI AGAR TIDAK CRASH DI RAILWAY)
# =====================================================================
async def run_single_bot(token: str, bot_name: str):
    app = ApplicationBuilder().token(token).build()
    
    # Conversation Handler Tebak Angka Mistik
    tebak_handler = ConversationHandler(
        entry_points=[CallbackQueryHandler(game_tebak_angka_start, pattern="^game_tebak_angka$")],
        states={
            STATE_TEBAK_ANGKA: [MessageHandler(filters.TEXT & ~filters.COMMAND, game_tebak_angka_process)]
        },
        fallbacks=[CommandHandler("cancel", cancel_handler)],
    )

    app.add_handler(CommandHandler("start", start_universal))
    app.add_handler(tebak_handler)
    app.add_handler(CallbackQueryHandler(callback_router))
    
    logger.info(f"Bot {bot_name} Berhasil Inisialisasi & Siap Polling!")
    
    # Menggunakan properti async run_polling bawaan PTTE v2 yang stabil
    await app.initialize()
    await app.start()
    await app.updater.start_polling(drop_pending_updates=True)
    
    # Menjaga bot tetap hidup selamanya di background loop
    try:
        while True:
            await asyncio.sleep(3600)
    finally:
        await app.updater.stop()
        await app.stop()
        await app.shutdown()

async def main():
    print("==================================================")
    print("🚀 MENJALANKAN DUA BOT GAME SEKALIGUS DALAM SATU SCRIPT!")
    print("==================================================")
    
    await asyncio.gather(
        run_single_bot(TOKEN_BOT_1, "BOT-UTAMA-1"),
        run_single_bot(TOKEN_BOT_2, "BOT-CADANGAN-2")
    )

if __name__ == '__main__':
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n❌ Kedua Bot Berhasil Dimatikan Manual, Aman Bos!")
