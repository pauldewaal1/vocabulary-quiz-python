from flask import Flask, render_template, request, redirect, url_for, jsonify
import sqlite3
import os

app = Flask(__name__)
DATABASE = os.environ.get('DATABASE_PATH', 'vocabulary.db')


def get_db():
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    """Initialize database with schema and default words if empty."""
    conn = get_db()
    conn.execute('''
        CREATE TABLE IF NOT EXISTS words (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            en TEXT NOT NULL,
            de TEXT NOT NULL,
            pron TEXT DEFAULT ''
        )
    ''')
    conn.commit()
    
    # Check if table is empty
    count = conn.execute('SELECT COUNT(*) FROM words').fetchone()[0]
    if count == 0:
        # Import default vocabulary
        default_words = [
            ("upstairs", "oben", "[ˈʌpˌsteəz]"),
            ("downstairs", "unten", "[ˌdaʊnˈsteəz]"),
            ("room", "der Raum", "[ruːm]"),
            ("why?", "warum?", "[waɪ]"),
            ("an hour", "eine Stunde", "[ən ˈaʊə]"),
            ("for", "für", "[fɔː]"),
            ("It/He/She isn't here", "Es/Er/Sie ist nicht hier", "[ˈɪznt hɪə]"),
            ("here", "hier", "[hɪə]"),
            ("Sorry", "Entschuldigung", "[ˈsɒri]"),
            ("Who?", "Wer?", "[huː]"),
            ("brother", "der Bruder", "[ˈbrʌðə]"),
            ("sister", "die Schwester", "[ˈsɪstə]"),
            ("Yes, I am", "Ja, das bin ich", "[jes aɪ æm]"),
            ("See you", "Bis bald", "[siː juː]"),
            ("You're lucky", "Du hast Glück", "[jɔː ˈlʌki]"),
            ("sure", "sicher", "[ʃʊə]"),
            ("smile", "das Lächeln", "[smaɪl]"),
            ("sometimes", "manchmal", "[ˈsʌmtaɪmz]"),
            ("weird", "komisch", "[wɪəd]"),
            ("at school", "in der Schule", "[æt skuːl]"),
            ("she's (she is)", "sie ist", "[ʃiːz]"),
            ("they aren't", "sie sind nicht", "[ðeɪ ɑːnt]"),
            ("they're", "sie sind", "[ðeə]"),
            ("divorced", "geschieden", "[dɪˈvɔːst]"),
            ("parents", "Eltern", "[ˈpeərənts]"),
            ("to listen", "zuhören", "[ˈlɪsn]"),
            ("phone", "das Telefon", "[fəʊn]"),
            ("message", "die Nachricht", "[ˈmesɪdʒ]"),
            ("free", "frei", "[friː]"),
            ("to hang out", "abhängen", "[hæŋ aʊt]"),
            ("at my place", "bei mir", "[æt maɪ pleɪs]"),
            ("place", "der Ort, der Platz", "[pleɪs]"),
            ("to know", "kennen", "[nəʊ]"),
            ("primary school", "die Grundschule", "[ˈpraɪməri skuːl]"),
            ("again", "noch einmal", "[əˈɡen]"),
            ("Good morning", "Guten Morgen", "[ɡʊd ˈmɔːnɪŋ]"),
            ("Here's / Here are", "Hier ist / Hier sind", "[hɪəz]"),
            ("parcel", "das Paket", "[ˈpɑːsl]"),
            ("very big", "sehr groß", "[ˈveri bɪɡ]"),
            ("to understand", "verstehen", "[ˌʌndəˈstænd]"),
            ("father", "der Vater", "[ˈfɑːðə]"),
            ("mother", "die Mutter", "[ˈmʌðə]"),
            ("useful", "nützlich", "[ˈjuːsfl]"),
            ("phrase", "der Satz", "[freɪz]"),
            ("grandma", "die Oma", "[ˈɡrænmɑː]"),
            ("grandpa", "der Opa", "[ˈɡrænpɑː]"),
            ("aunt", "die Tante", "[ɑːnt]"),
            ("uncle", "der Onkel", "[ˈʌŋkl]"),
            ("cousin", "der Cousin, die Cousine", "[ˈkʌzn]"),
            ("some", "einige", "[sʌm]"),
            ("English", "Englisch", "[ˈɪŋɡlɪʃ]"),
            ("word", "das Wort", "[wɜːd]"),
            ("like words in other languages", "wie Wörter in anderen Sprachen", "[laɪk wɜːdz]"),
            ("other", "andere", "[ˈʌðə]"),
            ("language", "die Sprache", "[ˈlæŋɡwɪdʒ]"),
            ("e.g.", "zum Beispiel", "[iːˈdʒiː]"),
            ("to help", "helfen", "[help]"),
            ("help", "die Hilfe", "[help]"),
            ("when", "wenn", "[wen]"),
            ("to learn", "lernen", "[lɜːn]"),
            ("to talk (to)", "reden (mit)", "[tɔːk]"),
            ("people", "Leute", "[ˈpiːpl]"),
            ("umbrella", "der Regenschirm", "[ʌmˈbrelə]"),
            ("to type", "tippen", "[taɪp]"),
            ("to pronounce", "aussprechen", "[prəˈnaʊns]"),
            ("then", "dann", "[ðen]"),
            ("to hear", "hören", "[hɪə]"),
            ("to say", "sagen", "[seɪ]"),
        ]
        conn.executemany('INSERT INTO words (en, de, pron) VALUES (?, ?, ?)', default_words)
        conn.commit()
    conn.close()


@app.route('/')
def index():
    """Main quiz page."""
    return render_template('quiz.html')


@app.route('/api/words')
def get_words():
    """Get all words as JSON for the quiz."""
    conn = get_db()
    words = conn.execute('SELECT id, en, de, pron FROM words').fetchall()
    conn.close()
    return jsonify([dict(w) for w in words])


@app.route('/admin')
def admin():
    """Admin page to manage words."""
    conn = get_db()
    words = conn.execute('SELECT id, en, de, pron FROM words ORDER BY en').fetchall()
    conn.close()
    return render_template('admin.html', words=words)


@app.route('/admin/add', methods=['POST'])
def add_word():
    """Add a new word."""
    en = request.form.get('en', '').strip()
    de = request.form.get('de', '').strip()
    pron = request.form.get('pron', '').strip()
    
    if en and de:
        conn = get_db()
        conn.execute('INSERT INTO words (en, de, pron) VALUES (?, ?, ?)', (en, de, pron))
        conn.commit()
        conn.close()
    
    return redirect(url_for('admin'))


@app.route('/admin/edit/<int:word_id>', methods=['POST'])
def edit_word(word_id):
    """Edit an existing word."""
    en = request.form.get('en', '').strip()
    de = request.form.get('de', '').strip()
    pron = request.form.get('pron', '').strip()
    
    if en and de:
        conn = get_db()
        conn.execute('UPDATE words SET en=?, de=?, pron=? WHERE id=?', (en, de, pron, word_id))
        conn.commit()
        conn.close()
    
    return redirect(url_for('admin'))


@app.route('/admin/delete/<int:word_id>', methods=['POST'])
def delete_word(word_id):
    """Delete a word."""
    conn = get_db()
    conn.execute('DELETE FROM words WHERE id=?', (word_id,))
    conn.commit()
    conn.close()
    return redirect(url_for('admin'))


if __name__ == '__main__':
    init_db()
    app.run(debug=True, host='0.0.0.0', port=8080)
