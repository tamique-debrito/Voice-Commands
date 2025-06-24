import speech_recognition as sr
import pyttsx3

class VoiceSpeaker:
    def __init__(self) -> None:
        self.engine = pyttsx3.init()
        self.engine.setProperty('rate', 150)
        self.engine.setProperty('volume', 0.9)
    
    def speak(self, text):
        self.engine.say(text)
        self.engine.runAndWait()


class MockVoiceSpeaker:
    def __init__(self) -> None:
        pass
    
    def speak(self, text):
        print(f"Speech: {text}")


class VoiceListener:
    def __init__(self) -> None:
        self.recognizer = sr.Recognizer()

    def get_voice(self):
        output = None
        while output is None:
            try:
                with sr.Microphone() as source2:
                    self.recognizer.adjust_for_ambient_noise(source2, duration=1)
                    audio2 = self.recognizer.listen(source2)

                    output = self.recognizer.recognize_google(audio2) #type: ignore
                print(f"User spoke command: {output}")
            except:
                #print("(restart voice input)")
                pass
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

if __name__ == "__main__":
    #v = VoiceListener()
    #print(v.get_voice())
    sp = VoiceSpeaker()
    sp.speak("I will move the basket from the desk to the closet. Then your friend can put the vitamins inside.")

    print("Done speaking")

    
    sp.speak("The task has now been completed")