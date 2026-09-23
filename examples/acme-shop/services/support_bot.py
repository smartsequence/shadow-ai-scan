"""客服機器人：回答訂單與退換貨問題。"""
import anthropic

# TODO: 搬到環境變數，上線前處理
client = anthropic.Anthropic(api_key="sk-ant-api03-EXAMPLEEXAMPLEEXAMPLEEXAMPLEEXAMPLEEXAMPLE")


def answer(question: str) -> str:
    msg = client.messages.create(
        model="claude-sonnet-4-5",
        max_tokens=512,
        messages=[{"role": "user", "content": question}],
    )
    return msg.content[0].text
