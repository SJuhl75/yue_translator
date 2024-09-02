from cantofilter import judge

print(judge('你喺邊度'))   # cantonese # black
print(judge('你在哪裏'))   # mandarin  # green
print(judge('是咁的'))     # mixed     # blue
print(judge('去學校讀書')) # neutral   # grey

#from canto_filters import judge

def format_text_with_judge(input_text):
    # Split the input text by spaces
    words = input_text.split()

    # Define a mapping of judge results to colors
    color_map = {
        "cantonese": "black",
        "mandarin": "green",
        "mixed": "blue",
        "neutral": "grey"
    }

    # Process each word/group
    formatted_words = []
    for word in words:
        # Apply the judge function to determine the language category
        category = judge(word)
        # Get the corresponding color
        color = color_map.get(category, "black")  # Default to black if category is not recognized
        # Format the word with the corresponding color
        formatted_word = f"<span style='color:{color};'>{word}</span>"
        formatted_words.append(formatted_word)

    # Join the formatted words back into a single string
    formatted_string = " ".join(formatted_words)
    return formatted_string

# Example usage
input_string = "你喺邊度 你在哪裏 是咁的 去學校讀書"
input_string = " 妈 咪 冇得 听 ， 所以 佢 我 想 攞 想 录 入 嗰 一个 ca 嘅 ， 因 为 佢 一 有 借 俾 佢 一个 食 细 一个 以 仔 入 部 听 。"
input_string = "你喺邊度 你在哪裏 是咁的 去學校讀書"
formatted_string = format_text_with_judge(input_string)
print(formatted_string)
