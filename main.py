# main.py
import sys
import os
from rag import ask_ollama, process_pdf, ask_from_pdf
from tools import convert_pdf_to_docx, convert_docx_to_pdf

def run_cmd():
    """Command-line interface with live streaming output"""
    print("🤖 LocalMind - Offline AI Assistant (CMD Mode)")
    print("=" * 60)
    print("Commands:")
    print("  'chat'      - NLP, Summarization, translation, maths, coding etc")
    print("  'askpdf'    - Load PDF and query it")
    print("  'pdf2doc'   - Convert a PDF file to a DOCX file")
    print("  'doc2pdf'   - Convert a DOCX file to a PDF file")
    print("  'exit'      - Quit the application")
    print("=" * 60)

    mode = "chat"
    pdf_loaded = False

    while True:
        try:
            # The prompt reflects the current mode
            if mode == "pdf" and pdf_loaded:
                prompt_text = "\n💬 You (PDF Mode): "
            else:
                prompt_text = "\n💬 You (Chat Mode): "
            user_input = input(prompt_text).strip()


            if not user_input:
                continue

            if user_input.lower() == "exit":
                print("👋 Goodbye!")
                break
            
            elif user_input.lower() == "chat":
                mode = "chat"
                print("✅ Switched to Chat mode.")
                continue
            
            elif user_input.lower() == "askpdf":
                mode = "pdf"
                # Handle file paths that are dragged-and-dropped (removes quotes)
                pdf_path = input("📄 Enter PDF path: ").strip().strip('"')
                
                if not pdf_path:
                    print("❌ No path provided.")
                    continue
                
                print("\n🔄 Processing PDF...")
                pdf_loaded = process_pdf(pdf_path)
                
                if pdf_loaded:
                    print("✅ PDF loaded successfully! You can now ask questions about it.")
                else:
                    print("❌ Failed to load PDF. Reverting to chat mode.")
                    mode = "chat"
                continue
            
            elif user_input.lower() == "pdf2doc":
                in_path = input("📄 Enter path of the PDF to convert: ").strip().strip('"')
                if not in_path:
                    print("❌ No input file provided.")
                    continue
                
                out_path = os.path.splitext(in_path)[0] + ".docx"
                print(f"🔄 Converting {os.path.basename(in_path)}...")
                success, message = convert_pdf_to_docx(in_path, out_path)
                if success:
                    print(f"✅ {message}")
                else:
                    print(f"❌ {message}")
                continue

            elif user_input.lower() == "doc2pdf":
                in_path = input("📄 Enter path of the DOCX to convert: ").strip().strip('"')
                if not in_path:
                    print("❌ No input file provided.")
                    continue

                out_path = os.path.splitext(in_path)[0] + ".pdf"
                print(f"🔄 Converting {os.path.basename(in_path)}...")
                success, message = convert_docx_to_pdf(in_path, out_path)
                if success:
                    print(f"✅ {message}")
                else:
                    print(f"❌ {message}")
                continue
            
            else:
                # Process user query
                print("\n🤖 AI: ", end="", flush=True)
                
                def stream_callback(text):
                    """Callback for live output streaming"""
                    print(text, end="", flush=True)
                
                if mode == "chat":
                    response = ask_ollama(user_input, model="phi3", callback=stream_callback)
                
                elif mode == "pdf":
                    if not pdf_loaded:
                        print("⚠️ No PDF loaded. Switching to chat mode.")
                        mode = "chat"
                        response = ask_ollama(user_input, model="phi3", callback=stream_callback)
                    else:
                        response = ask_from_pdf(user_input, callback=stream_callback)
                
                print()  # New line after response

        except KeyboardInterrupt:
            print("\n\n👋 Interrupted. Goodbye!")
            break
        except Exception as e:
            print(f"\n❌ An unexpected error occurred: {str(e)}")

def run_gui():
    """Launch GUI interface"""
    try:
        from gui import launch_gui
        launch_gui()
    except ImportError as e:
        print(f"❌ Error: Failed to import GUI module. {str(e)}")
        print("Make sure tkinter is installed.")
    except Exception as e:
        print(f"❌ Error launching GUI: {str(e)}")

if __name__ == "__main__":
    print("\n" + "=" * 60)
    print("  🧠 LocalMind - Offline AI Assistant")
    print("=" * 60 + "\n")
    
    mode = sys.argv[1].lower() if len(sys.argv) > 1 else "cmd"
    
    if mode == "gui":
        print("🖥️  Launching GUI mode...\n")
        print("Note: File conversion features are available in CMD mode.")
        run_gui()
    else:
        run_cmd()