"""
AI helper functions for content generation and enhancement.
"""
import os
import openai

# Configure OpenAI API
openai.api_key = os.environ.get('OPENAI_API_KEY')


def generate_blog_outline(topic, target_audience="general", word_count=1500):
    """
    Generate a blog post outline based on a topic.
    
    Args:
        topic (str): The main topic for the blog post
        target_audience (str): The target audience (e.g., beginners, professionals)
        word_count (int): Approximate target word count
        
    Returns:
        dict: Blog post outline with title, sections, and keywords
    """
    try:
        # Create prompt
        prompt = f"""
        Generate a detailed blog post outline about "{topic}" for a {target_audience} audience, 
        targeting approximately {word_count} words. Include a compelling title, introduction, 
        5-7 main sections with subpoints, and a conclusion. Also suggest 5-10 relevant keywords 
        for SEO purposes.
        
        Format the response as JSON with the following structure:
        {{
            "title": "The blog post title",
            "introduction": "Brief description of what the introduction should cover",
            "sections": [
                {{
                    "heading": "Section 1 heading",
                    "subpoints": ["Point 1", "Point 2"]
                }}
            ],
            "conclusion": "Brief description of what the conclusion should cover",
            "keywords": ["keyword1", "keyword2"]
        }}
        """
        
        # Get completion from OpenAI
        response = openai.Completion.create(
            model="gpt-4",
            prompt=prompt,
            max_tokens=1000,
            temperature=0.7
        )
        
        # Parse response
        return response.choices[0].text.strip()
    
    except Exception as e:
        return {
            "error": str(e),
            "message": "Failed to generate blog outline. Please check the OpenAI API key configuration."
        }


def generate_meta_description(content, max_length=160):
    """
    Generate an SEO-friendly meta description based on content.
    
    Args:
        content (str): The blog post content or excerpt
        max_length (int): Maximum length for the meta description
        
    Returns:
        str: SEO-friendly meta description
    """
    try:
        # Create prompt
        prompt = f"""
        Generate an SEO-friendly meta description based on the following content. 
        The meta description should be compelling, include relevant keywords, and be no longer than {max_length} characters.
        
        Content:
        {content[:2000]}  # Limit input content for token efficiency
        """
        
        # Get completion from OpenAI
        response = openai.Completion.create(
            model="gpt-4",
            prompt=prompt,
            max_tokens=100,
            temperature=0.5
        )
        
        # Parse and truncate response
        description = response.choices[0].text.strip()
        if len(description) > max_length:
            description = description[:max_length-3] + "..."
            
        return description
    
    except Exception as e:
        return f"Error generating meta description: {str(e)}"


def suggest_improvements(content):
    """
    Suggest improvements for blog content.
    
    Args:
        content (str): The blog post content
        
    Returns:
        dict: Suggestions for improving the content
    """
    try:
        # Create prompt
        prompt = f"""
        Analyze the following blog post content and provide specific suggestions for improvement in these areas:
        1. Overall structure and readability
        2. SEO optimization
        3. Engagement and hook
        4. Technical accuracy
        5. Call to action
        
        Format the response as JSON with suggestions for each area.
        
        Content:
        {content[:4000]}  # Limit input content for token efficiency
        """
        
        # Get completion from OpenAI
        response = openai.Completion.create(
            model="gpt-4",
            prompt=prompt,
            max_tokens=800,
            temperature=0.5
        )
        
        # Parse response
        return response.choices[0].text.strip()
    
    except Exception as e:
        return {
            "error": str(e),
            "message": "Failed to generate improvement suggestions. Please check the OpenAI API key configuration."
        }
