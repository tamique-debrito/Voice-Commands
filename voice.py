import speech_recognition as sr

class VoiceListener:
    def __init__(self) -> None:
        self.recognizer = sr.Recognizer()
        self.source = sr.Microphone()
        self.recognizer.adjust_for_ambient_noise(self.source, duration=1)
    
    def get_voice(self):
        audio = self.recognizer.listen(self.source)
        output = self.recognizer.recognize_google(audio) #type: ignore
        return output

        
class MockVoiceListener:
    def __init__(self) -> None:
        pass

    def get_voice(self):
        return input("User Input: ")

# r = sr.Recognizer()

# with sr.Microphone() as source2:
#     r.adjust_for_ambient_noise(source2, duration=1)
#     audio2 = r.listen(source2)

#     output = r.recognize_google(audio2) #type: ignore
#     output = output.lower()
#     print(output)

