import requests

def summarize_article(text, model="llama3.1:8b"):
    """
    Summarize the given article text using Ollama.
    
    :param text: The article text to summarize
    :param model: The Ollama model to use (default: "llama2:8b")
    :return: A bullet-point summary of the article
    """
    prompt = f"""INSTRUCTION: Summarize the following article in 3-5 bullet points. 
    Each bullet point should be a single sentence. Do not use nested bullet points or sub-points. 
    Start each bullet point with a dash (-) followed by a space.
    Only consider the article text provided below and nothing else.

    ARTICLE TEXT:
    {text}

    SUMMARY:"""
    
    try:
        response = requests.post(
            "http://localhost:11434/api/generate",
            json={
                "model": model,
                "prompt": prompt,
                "stream": False
            }
        )
        response.raise_for_status()
        result = response.json()
        summary = result['response'].strip()
        
        # Ensure the summary is in the correct format
        formatted_summary = format_bullet_points(summary)
        
        return formatted_summary
    except requests.RequestException as e:
        print(f"Error while summarizing article: {e}")
        return None

def format_bullet_points(text):
    """
    Ensure the summary is formatted as bullet points.
    """
    lines = text.split('\n')
    formatted_lines = []
    for line in lines:
        line = line.strip()
        if line and not line.startswith('-'):
            line = f"- {line}"
        formatted_lines.append(line)
    
    # Ensure we have at least 3 and at most 5 bullet points
    # while len(formatted_lines) < 3:
    #     formatted_lines.append("- Additional information not provided.")
    # formatted_lines = formatted_lines[:5]
    
    return '\n'.join(formatted_lines)

def format_summary(summary):
    """
    Format the summary with an "AI Summary" header and escape LaTeX special characters.
    
    :param summary: The bullet-point summary
    :return: Formatted summary with header, ready for LaTeX
    """
    latex_special_chars = {
        '&': r'\&',
        '%': r'\%',
        '$': r'\$',
        '#': r'\#',
        '_': r'\_',
        '{': r'\{',
        '}': r'\}',
        '~': r'\textasciitilde{}',
        '^': r'\^{}',
        '\\': r'\textbackslash{}',
    }
    
    escaped_summary = ''.join(latex_special_chars.get(c, c) for c in summary)
    
    formatted_summary = "\\textbf{AI Summary:}\n\\begin{itemize}\n"
    for line in escaped_summary.split('\n'):
        if line.strip().startswith('-'):
            formatted_summary += "\\item " + line.strip()[1:].strip() + "\n"
    formatted_summary += "\\end{itemize}\n\n"
    
    return formatted_summary

def format_summary_epub(summary):
    """
    Format the summary with an "AI Summary" header in HTML for EPUB.
    
    :param summary: The bullet-point summary
    :return: Formatted summary with header, ready for EPUB
    """
    formatted_summary = "<h3>AI Summary:</h3>\n<ul>\n"
    for line in summary.split('\n'):
        if line.strip().startswith('-'):
            formatted_summary += f"<li>{line.strip()[1:].strip()}</li>\n"
    formatted_summary += "</ul>\n"
    
    return formatted_summary