"""
Example examination formats and templates for the multi-agent system to reference
"""
from typing import Dict, Any, List


class ExamFormatExamples:
    """
    Repository of examination format examples and templates that agents can use as references
    """
    
    @staticmethod
    def get_academic_format_example() -> Dict[str, Any]:
        """Academic examination format example"""
        return {
            "format_type": "academic",
            "title_template": "{subject} - {level} Examination",
            "instructions_template": """
            INSTRUCTIONS FOR STUDENTS
            
            1. This examination contains {num_questions} questions worth a total of {total_points} points.
            2. You have {time_limit} minutes to complete this examination.
            3. Read each question carefully before answering.
            4. For multiple choice questions, select the BEST answer.
            5. For short answer questions, provide clear and concise responses.
            6. Show your work for calculation problems where applicable.
            7. Manage your time wisely.
            
            ACADEMIC INTEGRITY
            - This examination must be completed independently
            - No collaboration or external assistance is permitted
            - Violation of academic integrity policies will result in disciplinary action
            
            Good luck!
            """,
            "sections": [
                {
                    "name": "Part I: Multiple Choice",
                    "description": "Select the best answer for each question",
                    "question_types": ["multiple_choice"],
                    "point_value": 1,
                    "instructions": "Choose the letter corresponding to the best answer."
                },
                {
                    "name": "Part II: Short Answer",
                    "description": "Provide brief, clear answers",
                    "question_types": ["text"],
                    "point_value": 3,
                    "instructions": "Answer in 2-3 complete sentences."
                },
                {
                    "name": "Part III: Essay",
                    "description": "Comprehensive analysis and discussion",
                    "question_types": ["essay"],
                    "point_value": 10,
                    "instructions": "Write a well-organized essay of 300-500 words."
                }
            ],
            "grading_criteria": {
                "scale": "A-F",
                "breakdown": {
                    "A": 90,
                    "B": 80,
                    "C": 70,
                    "D": 60,
                    "F": 0
                },
                "rubric_elements": [
                    "Content accuracy and completeness",
                    "Critical thinking and analysis",
                    "Organization and clarity",
                    "Use of appropriate terminology"
                ]
            }
        }
    
    @staticmethod
    def get_professional_format_example() -> Dict[str, Any]:
        """Professional certification examination format example"""
        return {
            "format_type": "professional",
            "title_template": "{subject} Professional Certification Examination",
            "instructions_template": """
            PROFESSIONAL CERTIFICATION EXAMINATION
            
            EXAMINATION OVERVIEW
            This examination assesses your competency in {subject} as required for professional certification.
            
            EXAMINATION DETAILS
            - Total Questions: {num_questions}
            - Time Limit: {time_limit} minutes
            - Passing Score: 75%
            - Question Types: Multiple choice, scenario-based questions
            
            INSTRUCTIONS
            1. Answer all questions to the best of your ability
            2. Base your answers on current industry standards and best practices
            3. For scenario questions, select the MOST appropriate response
            4. Time management is crucial - pace yourself accordingly
            5. Review your answers if time permits
            
            IMPORTANT NOTES
            - This examination is computer-based and timed
            - You cannot return to previous questions once submitted
            - Calculators and reference materials are not permitted
            - Results will be available within 2 business days
            """,
            "sections": [
                {
                    "name": "Core Competencies",
                    "description": "Fundamental knowledge and skills",
                    "question_types": ["multiple_choice"],
                    "point_value": 2,
                    "weight": 0.6
                },
                {
                    "name": "Applied Scenarios",
                    "description": "Real-world application and problem-solving",
                    "question_types": ["multiple_choice"],
                    "point_value": 3,
                    "weight": 0.4
                }
            ],
            "grading_criteria": {
                "scale": "Pass/Fail",
                "passing_threshold": 0.75,
                "competency_areas": [
                    "Technical knowledge",
                    "Professional judgment",
                    "Ethical considerations",
                    "Industry standards compliance"
                ]
            }
        }
    
    @staticmethod
    def get_practice_format_example() -> Dict[str, Any]:
        """Practice test format example"""
        return {
            "format_type": "practice",
            "title_template": "{subject} Practice Test",
            "instructions_template": """
            PRACTICE TEST - {subject}
            
            PURPOSE
            This practice test is designed to help you assess your knowledge and prepare for the actual examination.
            
            TEST DETAILS
            - Questions: {num_questions}
            - Time: {time_limit} minutes
            - Format: Mixed question types
            - Feedback: Detailed explanations provided
            
            HOW TO USE THIS PRACTICE TEST
            1. Take the test under timed conditions for best practice
            2. Review all explanations, even for questions you answered correctly
            3. Identify areas where you need additional study
            4. Retake the test after studying to measure improvement
            
            TIPS FOR SUCCESS
            - Read questions carefully and completely
            - Eliminate obviously incorrect answers first
            - Don't spend too much time on any single question
            - Use the process of elimination for difficult questions
            """,
            "sections": [
                {
                    "name": "Knowledge Check",
                    "description": "Test your understanding of key concepts",
                    "question_types": ["multiple_choice", "true_false"],
                    "feedback_immediate": True
                },
                {
                    "name": "Application",
                    "description": "Apply your knowledge to practical situations",
                    "question_types": ["multiple_choice", "text"],
                    "feedback_immediate": True
                }
            ],
            "grading_criteria": {
                "scale": "Percentage",
                "performance_levels": {
                    "Excellent": 90,
                    "Good": 80,
                    "Satisfactory": 70,
                    "Needs Improvement": 60,
                    "Poor": 0
                },
                "feedback_detailed": True
            }
        }
    
    @staticmethod
    def get_question_format_examples() -> Dict[str, List[Dict[str, Any]]]:
        """Examples of well-formatted questions by type"""
        return {
            "multiple_choice": [
                {
                    "question_text": "Which of the following best describes the primary function of mitochondria in cells?",
                    "options": [
                        "Protein synthesis and modification",
                        "Energy production through cellular respiration",
                        "DNA replication and transcription",
                        "Waste removal and detoxification"
                    ],
                    "correct_answer": "Energy production through cellular respiration",
                    "explanation": "Mitochondria are known as the 'powerhouses' of the cell because they generate ATP through cellular respiration.",
                    "difficulty": "medium",
                    "bloom_level": "understand"
                },
                {
                    "question_text": "In project management, what is the critical path?",
                    "options": [
                        "The shortest sequence of activities in a project",
                        "The longest sequence of dependent activities that determines project duration",
                        "The most expensive sequence of activities",
                        "The sequence of activities with the highest risk"
                    ],
                    "correct_answer": "The longest sequence of dependent activities that determines project duration",
                    "explanation": "The critical path represents the longest sequence of activities that must be completed on time for the project to finish on schedule.",
                    "difficulty": "medium",
                    "bloom_level": "understand"
                }
            ],
            "true_false": [
                {
                    "question_text": "In statistical analysis, correlation implies causation.",
                    "correct_answer": False,
                    "explanation": "Correlation indicates a relationship between variables, but does not prove that one variable causes changes in another.",
                    "difficulty": "medium",
                    "bloom_level": "analyze"
                },
                {
                    "question_text": "The Python programming language is dynamically typed.",
                    "correct_answer": True,
                    "explanation": "Python is dynamically typed, meaning variable types are determined at runtime rather than compile time.",
                    "difficulty": "easy",
                    "bloom_level": "remember"
                }
            ],
            "text": [
                {
                    "question_text": "Define the term 'polymorphism' as it applies to object-oriented programming.",
                    "correct_answer": "Polymorphism allows objects of different classes to be treated as objects of a common base class while maintaining their own specific behaviors.",
                    "explanation": "Polymorphism enables a single interface to represent different underlying data types, allowing for flexible and reusable code.",
                    "difficulty": "medium",
                    "bloom_level": "understand"
                },
                {
                    "question_text": "What is the primary difference between renewable and non-renewable energy sources?",
                    "correct_answer": "Renewable energy sources can be naturally replenished within human timescales, while non-renewable sources are finite and depleted when used.",
                    "explanation": "Renewable sources like solar and wind can be continuously replenished, while non-renewable sources like fossil fuels take millions of years to form.",
                    "difficulty": "easy",
                    "bloom_level": "understand"
                }
            ],
            "essay": [
                {
                    "question_text": "Analyze the impact of artificial intelligence on modern healthcare, discussing both benefits and potential challenges. Support your analysis with specific examples.",
                    "correct_answer": "A comprehensive response should address: AI applications in diagnosis and treatment, improved efficiency and accuracy, challenges including data privacy and job displacement, ethical considerations, and specific examples such as medical imaging analysis or drug discovery.",
                    "explanation": "This essay should demonstrate understanding of AI technology, healthcare applications, critical analysis of impacts, and ability to provide concrete examples.",
                    "difficulty": "hard",
                    "bloom_level": "evaluate",
                    "rubric": {
                        "content_knowledge": 25,
                        "critical_analysis": 25,
                        "examples_and_evidence": 25,
                        "organization_and_clarity": 25
                    }
                }
            ]
        }
    
    @staticmethod
    def get_difficulty_guidelines() -> Dict[str, Dict[str, Any]]:
        """Guidelines for creating questions at different difficulty levels"""
        return {
            "easy": {
                "description": "Basic recall and comprehension",
                "bloom_levels": ["remember", "understand"],
                "characteristics": [
                    "Direct recall of facts or definitions",
                    "Simple comprehension of basic concepts",
                    "Straightforward application of formulas or procedures",
                    "Recognition of familiar patterns or examples"
                ],
                "example_verbs": ["define", "list", "identify", "describe", "explain"],
                "typical_points": 1
            },
            "medium": {
                "description": "Application and analysis",
                "bloom_levels": ["apply", "analyze"],
                "characteristics": [
                    "Application of knowledge to new situations",
                    "Analysis of relationships between concepts",
                    "Problem-solving using multiple steps",
                    "Comparison and contrast of ideas"
                ],
                "example_verbs": ["apply", "analyze", "compare", "solve", "calculate"],
                "typical_points": 2
            },
            "hard": {
                "description": "Synthesis and evaluation",
                "bloom_levels": ["evaluate", "create"],
                "characteristics": [
                    "Evaluation of arguments or solutions",
                    "Synthesis of information from multiple sources",
                    "Creation of original solutions or interpretations",
                    "Critical judgment and reasoning"
                ],
                "example_verbs": ["evaluate", "create", "design", "justify", "critique"],
                "typical_points": 3
            }
        }
    
    @staticmethod
    def get_bloom_taxonomy_guide() -> Dict[str, Dict[str, Any]]:
        """Guide to Bloom's taxonomy levels for question creation"""
        return {
            "remember": {
                "description": "Recall facts, basic concepts, and answers",
                "keywords": ["define", "duplicate", "list", "memorize", "recall", "repeat", "state"],
                "question_starters": ["What is...", "Who was...", "When did...", "Where is...", "List the..."],
                "example": "What is the chemical symbol for gold?"
            },
            "understand": {
                "description": "Explain ideas or concepts",
                "keywords": ["classify", "describe", "discuss", "explain", "identify", "locate", "recognize", "report", "select", "translate"],
                "question_starters": ["How would you explain...", "What does this mean...", "Give an example of..."],
                "example": "Explain why photosynthesis is important for life on Earth."
            },
            "apply": {
                "description": "Use information in new situations",
                "keywords": ["execute", "implement", "solve", "use", "demonstrate", "interpret", "operate", "schedule", "sketch"],
                "question_starters": ["How would you use...", "What would result if...", "How would you solve..."],
                "example": "Calculate the area of a triangle with a base of 8 cm and height of 6 cm."
            },
            "analyze": {
                "description": "Draw connections among ideas",
                "keywords": ["differentiate", "organize", "relate", "compare", "contrast", "distinguish", "examine", "experiment", "question", "test"],
                "question_starters": ["What are the parts...", "How is... related to...", "Why do you think..."],
                "example": "Compare and contrast renewable and non-renewable energy sources."
            },
            "evaluate": {
                "description": "Justify a stand or decision",
                "keywords": ["appraise", "argue", "defend", "judge", "select", "support", "value", "critique", "weigh"],
                "question_starters": ["Do you agree...", "What is your opinion...", "How would you prioritize..."],
                "example": "Evaluate the effectiveness of different strategies for reducing carbon emissions."
            },
            "create": {
                "description": "Produce new or original work",
                "keywords": ["design", "assemble", "construct", "conjecture", "develop", "formulate", "author", "investigate"],
                "question_starters": ["What would happen if...", "Can you design...", "How would you create..."],
                "example": "Design a sustainable urban transportation system for a city of 500,000 people."
            }
        }