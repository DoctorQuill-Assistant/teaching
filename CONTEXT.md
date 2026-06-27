# Teaching

This repository holds static learning materials for practical, beginner-friendly lessons across topics. It emphasizes small lessons, active recall, pronunciation support, and reusable learner-facing resources.

## Language

**Phrase Audio**:
A short text-to-speech generated audio clip attached to one learner-facing sentence or phrase for replay during a lesson.
_Avoid_: Audio lesson, pronunciation file, sound bite

**Audio Generation**:
The automated creation of Phrase Audio from lesson text as part of lesson production.
_Avoid_: Recording, manual narration

**Audio Selection**:
The lesson-authoring decision about which learner-facing phrases deserve Phrase Audio.
_Avoid_: Record everything, scrape every phrase

**Audio Manifest**:
A per-lesson file in a topic's audio area that lists the exact learner-facing phrases to turn into Phrase Audio, including stable clip identifiers and output files.
_Avoid_: Inferred phrase list, inline audio metadata

**Topic Audio Area**:
The per-topic folder that contains Audio Manifests and generated Phrase Audio for that topic.
_Avoid_: Global audio folder, lesson-local audio folder

**Good-Enough Audio**:
Phrase Audio that is clear enough for beginner replay and confidence-building, without requiring native-perfect pronunciation.
_Avoid_: Native-perfect audio, production narration

**Supported Audio Language**:
A lesson language for which the Audio Generation workflow has an approved local text-to-speech voice model.
_Avoid_: Any language, best-effort language

**Lesson Narration**:
A full-length recorded audio version of an entire lesson, intended for later listening rather than phrase-by-phrase replay.
_Avoid_: Audio lesson, podcast
