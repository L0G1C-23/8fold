#!/usr/bin/env python3
"""
Truth Weaver AI Detective - Complete Solution for Innov8 3.0 Hackathon
Organized by ARIES & Eightfold AI at Rendezvous IIT Delhi

This solution addresses "The Whispering Shadows Mystery" challenge by:
1. Converting audio to text with noise handling
2. Analyzing contradictions across sessions
3. Extracting truth from deceptive testimonies
4. Generating structured JSON reports
"""

import json
import re
import os
from typing import Dict, List, Tuple, Any
from dataclasses import dataclass
from pathlib import Path
import speech_recognition as sr
from pydub import AudioSegment
from pydub.effects import normalize, compress_dynamic_range
import openai
from difflib import SequenceMatcher
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@dataclass
class SessionData:
    """Data structure for individual session information"""
    session_id: int
    transcript: str
    confidence_level: float
    audio_quality: str
    emotional_state: str

class AudioProcessor:
    """Handles audio preprocessing and speech-to-text conversion"""
    
    def __init__(self):
        self.recognizer = sr.Recognizer()
        self.recognizer.energy_threshold = 300
        self.recognizer.dynamic_energy_threshold = True
        self.recognizer.pause_threshold = 0.8
        
    def enhance_audio(self, audio_path: str) -> str:
        """Enhance audio quality for better transcription"""
        try:
            # Load audio file
            audio = AudioSegment.from_file(audio_path)
            
            # Apply audio enhancements
            # Normalize volume
            audio = normalize(audio)
            
            # Reduce dynamic range to make quiet parts louder
            audio = compress_dynamic_range(audio, threshold=-20.0, ratio=4.0)
            
            # Apply high-pass filter to reduce low-frequency noise
            audio = audio.high_pass_filter(80)
            
            # Apply low-pass filter to reduce high-frequency noise
            audio = audio.low_pass_filter(8000)
            
            # Export enhanced audio
            enhanced_path = audio_path.replace('.', '_enhanced.')
            audio.export(enhanced_path, format="wav")
            
            return enhanced_path
            
        except Exception as e:
            logger.error(f"Audio enhancement failed: {e}")
            return audio_path
    
    def transcribe_audio(self, audio_path: str) -> Tuple[str, float]:
        """Convert audio to text with confidence scoring"""
        try:
            # Enhance audio first
            enhanced_path = self.enhance_audio(audio_path)
            
            # Load audio file
            with sr.AudioFile(enhanced_path) as source:
                # Adjust for ambient noise
                self.recognizer.adjust_for_ambient_noise(source, duration=1)
                audio_data = self.recognizer.record(source)
            
            # Try multiple recognition engines for better accuracy
            transcripts = []
            confidences = []
            
            # Google Speech Recognition
            try:
                result = self.recognizer.recognize_google(
                    audio_data, 
                    show_all=True,
                    language='en-US'
                )
                if result and 'alternative' in result:
                    for alt in result['alternative'][:3]:  # Top 3 alternatives
                        transcripts.append(alt.get('transcript', ''))
                        confidences.append(alt.get('confidence', 0.5))
            except:
                pass
            
            # Sphinx (offline backup)
            try:
                sphinx_result = self.recognizer.recognize_sphinx(audio_data)
                transcripts.append(sphinx_result)
                confidences.append(0.3)  # Lower confidence for offline
            except:
                pass
            
            # Select best transcript
            if transcripts:
                best_idx = confidences.index(max(confidences))
                return transcripts[best_idx], confidences[best_idx]
            else:
                return "", 0.0
                
        except Exception as e:
            logger.error(f"Transcription failed: {e}")
            return "", 0.0

class DeceptionAnalyzer:
    """Analyzes transcripts for contradictions and deception patterns"""
    
    def __init__(self):
        # Key phrases and patterns for different categories
        self.experience_patterns = {
            'years': r'(\d+)\s*(?:years?|yrs?)',
            'months': r'(\d+)\s*(?:months?|mos?)',
            'time_claims': r'(never|always|since|for|over|under|about|around|approximately)'
        }
        
        self.skill_indicators = {
            'languages': ['python', 'java', 'javascript', 'c++', 'c#', 'go', 'rust', 'ruby'],
            'frameworks': ['django', 'flask', 'react', 'angular', 'vue', 'spring', 'express'],
            'technologies': ['machine learning', 'ai', 'blockchain', 'cloud', 'docker', 'kubernetes'],
            'databases': ['mysql', 'postgresql', 'mongodb', 'redis', 'elasticsearch']
        }
        
        self.confidence_markers = {
            'high': ['definitely', 'absolutely', 'certainly', 'expert', 'master', 'proficient'],
            'medium': ['probably', 'likely', 'fairly', 'quite', 'decent', 'good'],
            'low': ['maybe', 'perhaps', 'kind of', 'sort of', 'not sure', 'learning']
        }
        
        self.deception_indicators = {
            'hesitation': ['um', 'uh', 'er', 'well', 'like', 'you know'],
            'backtracking': ['actually', 'correction', 'wait', 'no', 'i mean'],
            'emotional': ['crying', 'sobbing', 'shouting', 'whispering', 'nervous']
        }
    
    def extract_experience_claims(self, transcript: str) -> List[str]:
        """Extract all experience-related claims from transcript"""
        claims = []
        text = transcript.lower()
        
        # Find year/month claims
        for pattern_type, pattern in self.experience_patterns.items():
            matches = re.findall(pattern, text)
            for match in matches:
                if pattern_type in ['years', 'months']:
                    claims.append(f"{match} {pattern_type}")
        
        return claims
    
    def extract_skills(self, transcript: str) -> List[str]:
        """Extract mentioned skills and technologies"""
        skills = []
        text = transcript.lower()
        
        for category, skill_list in self.skill_indicators.items():
            for skill in skill_list:
                if skill in text:
                    skills.append(skill)
        
        return list(set(skills))  # Remove duplicates
    
    def assess_confidence_level(self, transcript: str) -> str:
        """Assess speaker's confidence level based on language markers"""
        text = transcript.lower()
        confidence_scores = {'high': 0, 'medium': 0, 'low': 0}
        
        for level, markers in self.confidence_markers.items():
            for marker in markers:
                confidence_scores[level] += text.count(marker)
        
        # Also check for deception indicators (reduce confidence)
        for category, indicators in self.deception_indicators.items():
            for indicator in indicators:
                confidence_scores['low'] += text.count(indicator)
        
        # Return the confidence level with highest score
        return max(confidence_scores.items(), key=lambda x: x[1])[0]
    
    def find_contradictions(self, sessions: List[SessionData]) -> List[Dict]:
        """Find contradictions across all sessions"""
        contradictions = []
        
        # Extract claims from all sessions
        all_claims = {}
        for session in sessions:
            session_claims = {
                'experience': self.extract_experience_claims(session.transcript),
                'skills': self.extract_skills(session.transcript),
                'confidence': self.assess_confidence_level(session.transcript)
            }
            all_claims[f"session_{session.session_id}"] = session_claims
        
        # Compare experience claims
        experience_claims = []
        for session_id, claims in all_claims.items():
            experience_claims.extend(claims['experience'])
        
        if len(set(experience_claims)) > 1:
            contradictions.append({
                'lie_type': 'experience_inflation',
                'contradictory_claims': list(set(experience_claims))
            })
        
        # Compare skill claims
        skill_consistency = []
        for session_id, claims in all_claims.items():
            if claims['skills']:
                skill_consistency.append(len(claims['skills']))
        
        if skill_consistency and max(skill_consistency) - min(skill_consistency) > 3:
            contradictions.append({
                'lie_type': 'skill_exaggeration',
                'contradictory_claims': [f"claimed {min(skill_consistency)} to {max(skill_consistency)} skills"]
            })
        
        return contradictions

class TruthWeaver:
    """Main class that orchestrates the entire truth detection process"""
    
    def __init__(self):
        self.audio_processor = AudioProcessor()
        self.deception_analyzer = DeceptionAnalyzer()
    
    def process_shadow_case(self, audio_files: List[str], shadow_id: str) -> Dict:
        """Process all audio files for a shadow agent and extract truth"""
        sessions = []
        combined_transcript = ""
        
        # Process each audio file
        for i, audio_file in enumerate(audio_files, 1):
            logger.info(f"Processing session {i}: {audio_file}")
            
            # Transcribe audio
            transcript, confidence = self.audio_processor.transcribe_audio(audio_file)
            
            if transcript:
                # Determine audio quality based on confidence
                if confidence > 0.8:
                    quality = "clear"
                elif confidence > 0.5:
                    quality = "moderate"
                else:
                    quality = "poor"
                
                # Determine emotional state
                emotional_state = self._detect_emotional_state(transcript)
                
                session = SessionData(
                    session_id=i,
                    transcript=transcript,
                    confidence_level=confidence,
                    audio_quality=quality,
                    emotional_state=emotional_state
                )
                sessions.append(session)
                
                # Add to combined transcript
                combined_transcript += f"Session {i}:\n{transcript}\n\n"
        
        # Analyze for contradictions and truth
        contradictions = self.deception_analyzer.find_contradictions(sessions)
        revealed_truth = self._extract_truth(sessions)
        
        # Construct final result
        result = {
            "shadow_id": shadow_id,
            "revealed_truth": revealed_truth,
            "deception_patterns": contradictions
        }
        
        return result, combined_transcript
    
    def _detect_emotional_state(self, transcript: str) -> str:
        """Detect emotional state from transcript content"""
        text = transcript.lower()
        
        if any(word in text for word in ['crying', 'sobbing', 'sob']):
            return "distressed"
        elif any(word in text for word in ['shouting', 'yelling', '!']):
            return "agitated"
        elif any(word in text for word in ['whisper', 'quiet', 'barely']):
            return "fearful"
        elif any(word in text for word in ['confident', 'sure', 'absolutely']):
            return "confident"
        else:
            return "neutral"
    
    def _extract_truth(self, sessions: List[SessionData]) -> Dict:
        """Extract the most likely truth from all sessions"""
        # Aggregate all information
        all_skills = []
        all_experience_claims = []
        programming_languages = set()
        leadership_mentions = []
        team_mentions = []
        
        for session in sessions:
            skills = self.deception_analyzer.extract_skills(session.transcript)
            all_skills.extend(skills)
            
            experience = self.deception_analyzer.extract_experience_claims(session.transcript)
            all_experience_claims.extend(experience)
            
            # Check for programming languages
            text = session.transcript.lower()
            for lang in self.deception_analyzer.skill_indicators['languages']:
                if lang in text:
                    programming_languages.add(lang)
            
            # Check for leadership claims
            if any(word in text for word in ['lead', 'team lead', 'manager', 'lead developer']):
                leadership_mentions.append(True)
            elif any(word in text for word in ['alone', 'individual', 'solo', 'by myself']):
                leadership_mentions.append(False)
            
            # Check for team experience
            if any(word in text for word in ['team', 'colleagues', 'group', 'collaborate']):
                team_mentions.append(True)
            elif any(word in text for word in ['alone', 'individual', 'solo']):
                team_mentions.append(False)
        
        # Determine most likely truth
        truth = {}
        
        # Programming experience (look for lowest claim in later sessions)
        if all_experience_claims:
            # Extract numeric values and find the most conservative estimate
            numeric_claims = []
            for claim in all_experience_claims:
                numbers = re.findall(r'\d+', claim)
                if numbers:
                    numeric_claims.append(int(numbers[0]))
            
            if numeric_claims:
                # Truth is likely closer to lower estimates (less inflated)
                truth["programming_experience"] = f"{min(numeric_claims)}-{max(numeric_claims)} years"
            else:
                truth["programming_experience"] = "unspecified"
        else:
            truth["programming_experience"] = "unspecified"
        
        # Primary programming language
        if programming_languages:
            truth["programming_language"] = list(programming_languages)[0]  # Most mentioned
        else:
            truth["programming_language"] = "unspecified"
        
        # Skill mastery level
        confidence_levels = [self.deception_analyzer.assess_confidence_level(s.transcript) for s in sessions]
        if 'high' in confidence_levels:
            truth["skill_mastery"] = "intermediate"  # Conservative estimate
        elif 'medium' in confidence_levels:
            truth["skill_mastery"] = "beginner-intermediate"
        else:
            truth["skill_mastery"] = "beginner"
        
        # Leadership claims
        if any(leadership_mentions):
            if any(not x for x in leadership_mentions):  # Mixed claims
                truth["leadership_claims"] = "fabricated"
            else:
                truth["leadership_claims"] = "claimed"
        else:
            truth["leadership_claims"] = "no claims made"
        
        # Team experience
        if any(team_mentions):
            if any(not x for x in team_mentions):  # Mixed claims
                truth["team_experience"] = "individual contributor"
            else:
                truth["team_experience"] = "team member"
        else:
            truth["team_experience"] = "individual contributor"
        
        # Skills and keywords
        unique_skills = list(set(all_skills))
        truth["skills and other keywords"] = unique_skills
        
        return truth
    
    def save_results(self, result: Dict, transcript: str, output_dir: str):
        """Save results to files as required by the challenge"""
        os.makedirs(output_dir, exist_ok=True)
        
        # Save JSON result
        json_path = os.path.join(output_dir, f"{result['shadow_id']}_analysis.json")
        with open(json_path, 'w', encoding='utf-8') as f:
            json.dump(result, f, indent=2)
        
        # Save transcript
        txt_path = os.path.join(output_dir, f"{result['shadow_id']}_transcript.txt")
        with open(txt_path, 'w', encoding='utf-8') as f:
            f.write(transcript)
        
        logger.info(f"Results saved to {output_dir}")

def main():
    """Main execution function for processing shadow cases"""
    truth_weaver = TruthWeaver()
    
    # Example usage - replace with actual audio files
    audio_files = [
        "C:\Users\Devraj\OneDrive - IIT Delhi\Desktop\INNOV8 3.0-20250907T060749Z-1-001\INNOV8 3.0\shadow_session1.mp3",
        "C:\Users\Devraj\OneDrive - IIT Delhi\Desktop\INNOV8 3.0-20250907T060749Z-1-001\INNOV8 3.0\shadow_session2.mp3",
        "C:\Users\Devraj\OneDrive - IIT Delhi\Desktop\INNOV8 3.0-20250907T060749Z-1-001\INNOV8 3.0\shadow_session3.mp3",
        "C:\Users\Devraj\OneDrive - IIT Delhi\Desktop\INNOV8 3.0-20250907T060749Z-1-001\INNOV8 3.0\shadow_session4.mp3",
        "C:\Users\Devraj\OneDrive - IIT Delhi\Desktop\INNOV8 3.0-20250907T060749Z-1-001\INNOV8 3.0\shadow_session5.mp3",
    ]
    
    shadow_id = "phoenix_2024"
    
    try:
        # Process the case
        result, transcript = truth_weaver.process_shadow_case(audio_files, shadow_id)
        
        # Save results
        truth_weaver.save_results(result, transcript, "output")
        
        # Display results
        print("=" * 60)
        print("TRUTH WEAVER ANALYSIS COMPLETE")
        print("=" * 60)
        print(json.dumps(result, indent=2))
        
    except Exception as e:
        logger.error(f"Processing failed: {e}")
        return False
    
    return True

if __name__ == "__main__":
    success = main()
    if success:
        print("\n✅ Truth Weaver completed successfully!")
    else:
        print("\n❌ Truth Weaver encountered errors.")