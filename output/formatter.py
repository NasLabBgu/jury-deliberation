"""Output formatting utilities for jury deliberation results."""

import os
import re
import tempfile
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Tuple, Optional


class OutputFormatter:
    """Handles formatting and saving of jury deliberation output."""
    
    def __init__(self):
        # Create output directory in project structure
        self.download_dir = self._setup_output_directory()
        print(f"Download directory: {self.download_dir}")
        
        # Color mapping for different speakers
        self.speaker_colors = {
            "Moderator": "#2E8B57",      # Sea Green
            "Final_Verdict": "#8B0000",   # Dark Red
            # Default juror colors (will be assigned dynamically)
            "default_colors": [
                "#4169E1",  # Royal Blue
                "#DC143C",  # Crimson
                "#FF8C00",  # Dark Orange
                "#9932CC",  # Dark Orchid
                "#228B22",  # Forest Green
                "#FF1493",  # Deep Pink
                "#8B4513",  # Saddle Brown
                "#00CED1",  # Dark Turquoise
            ]
        }
        
        self.juror_colors: Dict[str, str] = {}
        self.output_buffer: List[str] = []

    def _setup_output_directory(self) -> str:
        """Set up the output directory in the project structure.
        
        Returns:
            Path to the output directory
        """
        # Get the project root directory (where main.py is located)
        project_root = Path(__file__).parent.parent
        
        # Create deliberations subdirectory in output folder
        deliberations_dir = project_root / "output" / "deliberations"
        
        # Create directory if it doesn't exist
        deliberations_dir.mkdir(parents=True, exist_ok=True)
        
        return str(deliberations_dir)

    def assign_juror_colors(self, jury_names: List[str]) -> Dict[str, str]:
        """Assign colors to jury members.
        
        Args:
            jury_names: List of jury member names
            
        Returns:
            Dictionary mapping jury names to color codes
        """
        colors = {}
        available_colors = self.speaker_colors["default_colors"]

        for i, name in enumerate(jury_names):
            if i < len(available_colors):
                colors[name] = available_colors[i]
            else:
                # If more jurors than colors, cycle through
                colors[name] = available_colors[i % len(available_colors)]

        self.juror_colors = colors
        return colors

    def format_speaker_output(self, speaker: str, content: str) -> str:
        """Format speaker output with colors for markdown.
        
        Args:
            speaker: Name of the speaker
            content: Content of the message
            
        Returns:
            Formatted string with HTML color styling
        """
        if speaker in self.juror_colors:
            color = self.juror_colors[speaker]
        elif speaker in self.speaker_colors:
            color = self.speaker_colors[speaker]
        else:
            color = "#000000"  # Default black

        return f'<span style="color: {color}"><strong>{speaker}:</strong></span> {content}'

    def clean_filename_for_output(self, filepath: Optional[str]) -> str:
        """Extract clean filename without extension and path.
        
        Args:
            filepath: Original file path
            
        Returns:
            Clean filename suitable for output files
        """
        if filepath is None:
            return "unknown"

        # Get just the filename without path
        filename = filepath.split('/')[-1].split('\\')[-1]

        # Remove extension
        filename = filename.rsplit('.', 1)[0]

        # Replace spaces and special characters with underscores
        filename = filename.replace(' ', '_').replace('-', '_')

        # Remove any non-alphanumeric characters except underscores
        filename = re.sub(r'[^a-zA-Z0-9_]', '', filename)

        return filename

    def add_output(self, speaker: str, content: str):
        """Add formatted output to the buffer.
        
        Args:
            speaker: Name of the speaker
            content: Content of the message
        """
        formatted_output = self.format_speaker_output(speaker, content)
        self.output_buffer.append(formatted_output)

    def save_deliberation_to_markdown(
        self, 
        case_details: str, 
        filename: Optional[str] = None,
        jury_filename: Optional[str] = None,
        case_filename: Optional[str] = None,
        scenario_number: Optional[int] = None,
        total_rounds: int = 3
    ) -> Optional[str]:
        """Save deliberation output to a markdown file with enhanced naming.
        
        Args:
            case_details: The case details text
            filename: Custom filename (optional)
            jury_filename: Name of the jury file used
            case_filename: Name of the case file used
            scenario_number: Scenario number if applicable
            total_rounds: Number of deliberation rounds
            
        Returns:
            Full path to saved file or None if failed
        """
        if filename is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

            # Build filename components
            jury_part = self.clean_filename_for_output(jury_filename) if jury_filename else "default_jury"
            case_part = self.clean_filename_for_output(case_filename) if case_filename else "direct_case"
            scenario_part = f"scenario{scenario_number}" if scenario_number else "full"

            filename = f"deliberation_{jury_part}_{case_part}_{scenario_part}_{timestamp}.md"

        # Save to download directory
        full_filepath = os.path.join(self.download_dir, filename)

        # Create markdown content
        markdown_content = f"""# Jury Deliberation Report

**Generated on:** {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}

**Configuration:**
- Jury File: {jury_filename or "Default jury members"}
- Case File: {case_filename or "Direct input"}
- Scenario: {scenario_number if scenario_number else "Full case"}
- Rounds: {total_rounds}

## Case Details

{case_details}

---

## Deliberation Process

"""

        # Add all the captured output
        for line in self.output_buffer:
            markdown_content += line + "\n\n"

        # Add color legend
        markdown_content += "\n---\n\n## Color Legend\n\n"

        # Get current juror colors and add all speakers to legend
        all_colors = {**self.juror_colors, **self.speaker_colors}

        for speaker, color in all_colors.items():
            if speaker != "default_colors":
                markdown_content += f'<span style="color: {color}"><strong>{speaker}</strong></span>\n\n'

        # Save to file
        try:
            with open(full_filepath, 'w', encoding='utf-8') as f:
                f.write(markdown_content)
            print(f"📄 Deliberation saved to: {full_filepath}")
            return full_filepath
        except Exception as e:
            print(f"❌ Error saving deliberation: {e}")
            return None

    def get_download_directory(self) -> str:
        """Get the download directory path.
        
        Returns:
            Path to the download directory
        """
        return self.download_dir
    
    def get_relative_output_path(self) -> str:
        """Get the relative path to the output directory from project root.
        
        Returns:
            Relative path to the output directory
        """
        project_root = Path(__file__).parent.parent
        output_path = Path(self.download_dir)
        try:
            return str(output_path.relative_to(project_root))
        except ValueError:
            # If relative path can't be computed, return absolute path
            return str(output_path)

    def list_download_files(self) -> List[Tuple[str, str]]:
        """List all files available in the download directory.
        
        Returns:
            List of tuples containing (filename, full_path)
        """
        try:
            if os.path.exists(self.download_dir):
                files = [f for f in os.listdir(self.download_dir) if f.endswith('.md')]
                return [(f, os.path.join(self.download_dir, f)) for f in sorted(files, reverse=True)]
            return []
        except Exception as e:
            print(f"❌ Error listing download files: {e}")
            return []

    def clear_buffer(self):
        """Clear the output buffer."""
        self.output_buffer.clear()

    def get_buffer(self) -> List[str]:
        """Get the current output buffer.
        
        Returns:
            List of formatted output strings
        """
        return self.output_buffer.copy()


# Global formatter instance
output_formatter = OutputFormatter()
