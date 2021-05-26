from flask import Flask, render_template
from flask import request, escape
from google.cloud import texttospeech

app = Flask(__name__)

@app.route("/")
def index():
  input_text_user = str(escape(request.args.get("input_text", "")))
  if input_text_user:
    print("Text content: " + input_text_user)
    stored_file = synthesize_audio(input_text_user)
    result = render_template('index.html', the_audio=stored_file)
    # """<figure>
    # <figcaption>Listen to your audio:</figcaption>
    # <audio
    #     controls
    #     src="https://storage.googleapis.com/test_text_and_audio/backyard_rain_ds.wav">
    #         Your browser does not support the <code>audio</code> element.
    # </audio>
    # </figure>"""
  else:
    result = ""
  return """
  <form>
      <fieldset><legend>Text to Speech</legend><br/>
      <label for="input_text"><span>Input Text: </span><input type="text" name="input_text"></label>
      <label><span> </span><input type="submit" value="Synthesize" /></label>
      </fieldset></form><br/><br/>""" + result

# @app.route("/<string:input_text>")
def synthesize_audio(input_text):
  """Creates the speech for a given string"""
  try:
    # Instantiates a client
    client = texttospeech.TextToSpeechClient()
    # Set the text input to be synthesized
    # synthesis_input = texttospeech.types.SynthesisInput(str(input_text))
    synthesis_input = {"text": input_text}
    # Build the voice request, select the language code ("en-US") and the ssml
    # voice gender ("neutral")
    voice = texttospeech.types.VoiceSelectionParams(
        language_code='en-US',
        ssml_gender=texttospeech.enums.SsmlVoiceGender.FEMALE)
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
