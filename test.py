from session.memory import (
    init_session_collection,
    create_session,
    update_profile_from_text,
    clear_session_memory
)

from retrieval.search import (
    discover_schemes_for_session,
    scheme_action_menu,
    get_last_results
)

# -----------------------------
# MULTIMODAL INPUT MODULES
# -----------------------------
from input.audio_input import transcribe_audio
from input.mic_input import record_from_mic
from input.push_to_talk import push_to_talk

from input.upload_pdf import ingest_pdf_for_session
from input.upload_image import ingest_image_for_session

from retrieval.search_docs import search_documents
from retrieval.search_user_docs import search_user_docs

TRIGGER = "what schemes can benefit me?"


def read_input():
    """
    Reads user input.
    Allows exit from anywhere.
    """
    value = input(">> ").strip()
    if value.lower() == "exit":
        raise SystemExit
    return value


def main():
    # -----------------------------
    # INIT SESSION
    # -----------------------------
    init_session_collection()
    session_id = create_session()

    # -----------------------------
    # STARTUP BANNER
    # -----------------------------
    print("\nSession started.")
    print("Describe yourself freely.")
    print(f"Type '{TRIGGER}' to see schemes.")
    print("\nInput options:")
    print("• Text input (default)")
    print("• audio <path>        → audio file")
    print("• record              → timed mic recording")
    print("• push                → push-to-talk")
    print("\nUpload options:")
    print("• upload pdf <path>")
    print("• upload image <path>")
    print("\nOther commands:")
    print("• clear memory")
    print("• exit\n")

    try:
        while True:
            user_input = read_input()

            # -----------------------------
            # CLEAR MEMORY
            # -----------------------------
            if user_input.lower() == "clear memory":
                print(clear_session_memory(session_id))
                continue

            # -----------------------------
            # USER UPLOAD: PDF
            # -----------------------------
            if user_input.lower().startswith("upload pdf "):
                path = user_input[11:].strip()
                try:
                    success = ingest_pdf_for_session(session_id, path)
                    if success:
                        print("PDF uploaded and indexed for this session.")
                    else:
                        print("PDF upload completed (OCR not applied).")
                except Exception as e:
                    print(f"PDF upload failed: {e}")
                continue

            # -----------------------------
            # USER UPLOAD: IMAGE
            # -----------------------------
            if user_input.lower().startswith("upload image "):
                path = user_input[13:].strip()
                try:
                    success = ingest_image_for_session(session_id, path)
                    if success:
                        print("Image uploaded and indexed for this session.")
                    else:
                        print("Image upload completed (OCR not applied).")
                except Exception as e:
                    print(f"Image upload failed: {e}")
                continue

            # -----------------------------
            # AUDIO FILE INPUT
            # -----------------------------
            if user_input.lower().startswith("audio "):
                path = user_input[6:].strip()
                try:
                    text = transcribe_audio(path)
                    print(f"[Transcribed]: {text}")
                    print(update_profile_from_text(session_id, text))
                except Exception as e:
                    print(f"Audio processing failed: {e}")
                continue

            # -----------------------------
            # TIMED MIC RECORD
            # -----------------------------
            if user_input.lower() == "record":
                try:
                    path = record_from_mic()
                    text = transcribe_audio(path)
                    print(f"[Transcribed]: {text}")
                    print(update_profile_from_text(session_id, text))
                except Exception as e:
                    print(f"Mic recording failed: {e}")
                continue

            # -----------------------------
            # PUSH TO TALK
            # -----------------------------
            if user_input.lower() == "push":
                try:
                    path = push_to_talk()
                    text = transcribe_audio(path)
                    print(f"[Transcribed]: {text}")
                    print(update_profile_from_text(session_id, text))
                except Exception as e:
                    print(f"Push-to-talk failed: {e}")
                continue

            # -----------------------------
            # DISCOVER SCHEMES
            # -----------------------------
            if user_input.lower() == TRIGGER:
                discover_schemes_for_session(session_id)

                while True:
                    results = get_last_results()
                    if not results:
                        break

                    print("\nOptions:")
                    print("• Enter scheme number")
                    print("• docs → official + uploaded document references")
                    print("• back → profile input")
                    print("• clear memory")
                    print("• exit\n")

                    choice = read_input().lower()

                    if choice == "back":
                        break

                    if choice == "clear memory":
                        print(clear_session_memory(session_id))
                        break

                    if choice == "docs":
                        search_documents("government scheme eligibility and guidelines")
                        search_user_docs(session_id, "government scheme eligibility")
                        continue

                    if choice.isdigit():
                        idx = int(choice) - 1
                        if 0 <= idx < len(results):
                            action = scheme_action_menu(idx)
                            if action == "BACK_TO_LIST":
                                discover_schemes_for_session(session_id)
                        else:
                            print("Invalid scheme number.")
                    else:
                        print("Invalid input.")

            # -----------------------------
            # NORMAL PROFILE UPDATE
            # -----------------------------
            else:
                print(update_profile_from_text(session_id, user_input))

    except SystemExit:
        print("\nExiting. Goodbye.\n")


if __name__ == "__main__":
    main()
