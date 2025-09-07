from truth_weaver import TruthWeaver

# Initialize the system
truth_weaver = TruthWeaver()

# Process a case
result, transcript = truth_weaver.process_shadow_case(
    audio_files=[
        r"C:\Users\Devraj\OneDrive - IIT Delhi\Desktop\INNOV8 3.0-20250907T060749Z-1-001\INNOV8 3.0\shadow_session1.mp3",
        r"C:\Users\Devraj\OneDrive - IIT Delhi\Desktop\INNOV8 3.0-20250907T060749Z-1-001\INNOV8 3.0\shadow_session2.mp3",
        r"C:\Users\Devraj\OneDrive - IIT Delhi\Desktop\INNOV8 3.0-20250907T060749Z-1-001\INNOV8 3.0\shadow_session3.mp3",
        r"C:\Users\Devraj\OneDrive - IIT Delhi\Desktop\INNOV8 3.0-20250907T060749Z-1-001\INNOV8 3.0\shadow_session4.mp3",
        r"C:\Users\Devraj\OneDrive - IIT Delhi\Desktop\INNOV8 3.0-20250907T060749Z-1-001\INNOV8 3.0\shadow_session5.mp3",
        ],
    shadow_id="test_shadow"
)

# Save results
truth_weaver.save_results(result, transcript, "output_directory")