import dbus
import json
import regex as re
from dbus.mainloop.glib import DBusGMainLoop
from gi.repository import GLib
from datetime import datetime
from sakura_translator import SakuraTranslator

APP_ID = "io.github.waylyrics.Waylyrics"
OBJECT_PATH = "/io/github/waylyrics/Waylyrics"

translator = SakuraTranslator()

ja_pattern = re.compile(r'([\p{IsHan}\p{IsHira}\p{IsKatakana}]+)', re.UNICODE)
ja_pure_pattern = re.compile(r'([\p{IsHira}\p{IsKatakana}]+)', re.UNICODE)


def check_is_japanese(text):
    # Check if over 80% of the characters are Japanese
    japanese_count = 0
    japanese_pure_count = 0

    for match in ja_pure_pattern.finditer(text):
        japanese_pure_count += len(match.group())
    for match in ja_pattern.finditer(text):
        japanese_count += len(match.group())

    return japanese_pure_count > 0 and japanese_count / len(text) > 0.7


def parse_json_for_translation(json_str):
    data = json.loads(json_str)
    lyrics = data['olyric']['content']
    tlyric_exists = data['tlyric']['type'] != "None"

    texts = []
    empty_lines_indices = []

    # Extract text and note the indices of empty lines
    for index, lyric in enumerate(lyrics):
        text = lyric['text']
        if text == "":
            empty_lines_indices.append(index)
        texts.append(text)

    # Join texts, preserving all lines (including empty ones) for batch processing
    translation_input = "\n".join(texts)
    return translation_input, empty_lines_indices, lyrics, tlyric_exists


def split_into_batches(text, max_tokens=300):
    lines = text.split('\n')
    batches = []
    current_batch = []
    current_token_count = 0

    for line in lines:
        line_token_count = len(line)

        if current_token_count + line_token_count > max_tokens:
            if current_batch:
                batches.append("\n".join(current_batch))
            current_batch = []
            current_token_count = 0

        current_batch.append(line)
        current_token_count += line_token_count

        if not line:
            batches.append("\n".join(current_batch))
            current_batch = []
            current_token_count = 0

    if current_batch:
        batches.append("\n".join(current_batch))

    return batches


def translate_batch(batch):
    queries = batch.strip().split('\n')
    translations = translator._translate('JPN', 'CHS', queries)
    return '\n'.join(translations)


def reconstruct_with_newlines(translated_batches, empty_lines_indices, original_lyrics):
    lines = []
    batch_index = 0
    line_index = 0

    for index in range(len(original_lyrics)):
        if index in empty_lines_indices:
            lines.append("")
        else:
            if batch_index < len(translated_batches):
                batch_lines = translated_batches[batch_index].split('\n')
                if line_index < len(batch_lines):
                    lines.append(batch_lines[line_index])
                    line_index += 1
                else:
                    batch_index += 1
                    line_index = 0
                    if batch_index < len(translated_batches):
                        batch_lines = translated_batches[batch_index].split('\n')
                        lines.append(batch_lines[line_index])
                        line_index += 1

    translated_lyrics = []
    for index, line in enumerate(lines):
        translated_lyrics.append({
            "text": line,
            "start_time": original_lyrics[index]["start_time"]
        })

    return translated_lyrics


def on_new_lyric_cache(cache_path):
    print(f"Received NewLyricCache signal with cache path: {cache_path}")
    with open(cache_path, 'r') as file:
        json_data = json.load(file)

    translation_input, empty_lines_indices, original_lyrics, tlyric_exists = parse_json_for_translation(
        json.dumps(json_data))

    if not check_is_japanese(translation_input) or tlyric_exists:
        print("Not japanese lyrics or translation already exists. Skipping...")
        return

    batches = split_into_batches(translation_input)

    translated_batches = []
    for batch in batches:
        translated_text = translate_batch(batch)
        translated_batches.append(translated_text)

    translated_lyrics = reconstruct_with_newlines(translated_batches, empty_lines_indices, original_lyrics)

    current_datetime = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    json_data['tlyric'] = {
        "type": "LineTimestamp",
        "content": translated_lyrics,
        "provider": "SakuraTranslator",
        "translationDate": current_datetime
    }

    with open(cache_path, 'w') as file:
        json.dump(json_data, file, indent=4, ensure_ascii=False)

    print("Translation complete. Updated JSON file saved.")

    bus = dbus.SessionBus()
    waylyrics_object = bus.get_object(APP_ID, OBJECT_PATH)
    waylyrics_actions = dbus.Interface(waylyrics_object, 'org.gtk.Actions')
    waylyrics_actions.Activate('reload-lyric', [], {})


def main():
    DBusGMainLoop(set_as_default=True)

    bus = dbus.SessionBus()

    # Subscribe to the NewLyricCache signal
    bus.add_signal_receiver(
        on_new_lyric_cache,
        dbus_interface=APP_ID,
        signal_name="NewLyricCache",
        path=OBJECT_PATH,
    )

    # Run the event loop indefinitely
    loop = GLib.MainLoop()
    loop.run()


if __name__ == "__main__":
    main()
