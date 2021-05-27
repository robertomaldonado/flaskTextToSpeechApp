from flask import Flask, render_template
from flask import request, escape
from google.cloud import texttospeech
import random

app = Flask(__name__)

@app.route("/")
def index():
  input_text_user = str(escape(request.args.get("input_text", "")))
  gender = str(escape(request.args.get("gender", "")))
  if input_text_user:
    print("Text content: " + input_text_user)
    print("Audio gender: " + gender)
    stored_file = synthesize_audio(input_text_user, gender)
    result = render_template('index.html', the_audio=stored_file)
  else:
    result = ""
  return """
    <form>
      <fieldset><legend>Text to Speech</legend><br/>
      <label for="input_text"><span>Input Text: </span><input type="text" name="input_text"></label>
      <label for="gender"><span>Called Profile (gender): </span><input type="text" name="gender"></label>
      <label><span> </span><input type="submit" value="Synthesize" /></label>
      </fieldset>
    </form><br/><br/>""" + result

# @app.route("/<string:input_text>")
def synthesize_audio(input_text, gender):
  """Creates the speech for a given string"""
  # Instantiates a client
  client = texttospeech.TextToSpeechClient()
  SSML_MALE="1"
  SSML_FEMALE="2"
  # """ Creates a list with all of the english voices """
  allowed_language_codes = ["en-US", "en-AU", "en-IN", "en-GB"]
  voices_list = list(client.list_voices().voices)
  english_voices = [voice for voice in voices_list if voice.language_codes[0] in allowed_language_codes]
  
  # """ Splits the list into male and female voices """
  male_en_voices = list()
  female_en_voices = list()
  for voice in english_voices:
      if str(voice.ssml_gender) == SSML_FEMALE:
        female_en_voices.append(voice)
      elif str(voice.ssml_gender) == SSML_MALE:
        male_en_voices.append(voice)
  try:
    chosen_voice = random.choice(male_en_voices) if gender == "male" else random.choice(female_en_voices)
    
    # Set the text input to be synthesized
    # synthesis_input = texttospeech.types.SynthesisInput(str(input_text))
    synthesis_input = {"text": input_text}
    # Build the voice request, select the language code ("en-US") and the ssml
    # voice gender ("neutral")
    voice = texttospeech.types.VoiceSelectionParams(
        language_code=chosen_voice.language_codes[0],
        ssml_gender = chosen_voice.ssml_gender)
    # Select the type of audio file you want returned
    audio_config = texttospeech.types.AudioConfig(
        audio_encoding=texttospeech.enums.AudioEncoding.LINEAR16)
    # Perform the text-to-speech request on the text input with the selected
    # voice parameters and audio file type
    resp = client.synthesize_speech(synthesis_input, voice, audio_config)
    # The response's audio_content is binary.
    with open('static/output.wav', 'wb') as out:
      # Write the response to the output file.
      out.write(resp.audio_content)
      print('Audio content written to file "static/output.wav"')
    return "output.wav"
  except ValueError:
    return "Invalid entry"

if __name__ == "__main__":
  app.run(host="127.0.0.1", port=8080, debug=True)
