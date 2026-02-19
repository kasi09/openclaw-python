"""
Example usage of OpenClaw Python Skills.

This script demonstrates how to:
1. Create a skill instance
2. Execute skill actions
3. Handle results and errors
"""

import asyncio
from openclaw_python_skill import SkillInput
from openclaw_python_skill.skills import TextAnalyzerSkill


async def main():
    """Run example demonstrations."""
    
    # Initialize the text analyzer skill
    skill = TextAnalyzerSkill()
    
    print("=" * 60)
    print("OpenClaw Python Skills - Text Analyzer Examples")
    print("=" * 60)
    
    # Example 1: Text Statistics
    print("\n📊 Example 1: Text Statistics Analysis")
    print("-" * 60)
    
    stats_input = SkillInput(
        action="text_stats",
        parameters={
            "text": "Hello world! This is an example. OpenClaw is awesome!"
        }
    )
    
    stats_result = await skill.execute(stats_input)
    print(f"Status: {'✅ Success' if stats_result.success else '❌ Failed'}")
    print(f"Result: {stats_result.result}")
    print(f"Execution time: {stats_result.metadata['execution_time_ms']:.2f}ms")
    
    # Example 2: Sentiment Analysis
    print("\n😊 Example 2: Sentiment Analysis")
    print("-" * 60)
    
    sentiment_input = SkillInput(
        action="text_sentiment",
        parameters={
            "text": "I absolutely love this! It's great, excellent, and amazing!"
        }
    )
    
    sentiment_result = await skill.execute(sentiment_input)
    print(f"Status: {'✅ Success' if sentiment_result.success else '❌ Failed'}")
    print(f"Sentiment: {sentiment_result.result['sentiment']}")
    print(f"Positive words: {sentiment_result.result['positive_words']}")
    print(f"Negative words: {sentiment_result.result['negative_words']}")
    print(f"Confidence: {sentiment_result.result['confidence']:.2f}")
    
    # Example 3: Pattern Detection
    print("\n🔍 Example 3: Pattern Detection")
    print("-" * 60)
    
    patterns_input = SkillInput(
        action="text_patterns",
        parameters={
            "text": (
                "Contact us at support@openclaw.ai or admin@openclaw.ai. "
                "Visit https://openclaw.ai for more info. "
                "Call us at 555-123-4567."
            )
        }
    )
    
    patterns_result = await skill.execute(patterns_input)
    print(f"Status: {'✅ Success' if patterns_result.success else '❌ Failed'}")
    print(f"URLs found: {patterns_result.result['urls']}")
    print(f"Emails found: {patterns_result.result['emails']}")
    print(f"Phone numbers found: {patterns_result.result['phone_numbers']}")
    print(f"Total patterns: {patterns_result.result['patterns_found']}")
    
    # Example 4: Error Handling
    print("\n⚠️  Example 4: Error Handling")
    print("-" * 60)
    
    error_input = SkillInput(
        action="text_stats",
        parameters={}  # Missing required 'text' parameter
    )
    
    error_result = await skill.execute(error_input)
    print(f"Status: {'✅ Success' if error_result.success else '❌ Failed'}")
    if not error_result.success:
        print(f"Error: {error_result.error}")
    
    # Example 5: Skill Metadata
    print("\n📋 Example 5: Skill Metadata")
    print("-" * 60)
    
    metadata = skill.describe()
    print(f"Skill Name: {metadata['name']}")
    print(f"Version: {metadata['version']}")
    print(f"Description: {metadata['description'][:100]}...")
    
    print("\n" + "=" * 60)
    print("Examples completed!")
    print("=" * 60)


if __name__ == "__main__":
    asyncio.run(main())
