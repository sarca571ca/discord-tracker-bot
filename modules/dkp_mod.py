# Build this function out to handle calculating dkp and listen for late x's in the channel
async def calculate_DKP(channel, channel_name, w):
    await channel.send(".........!DKPEport.........")
    # messages = []
    # authors_without_number = set()

    # async for message in channel.history(limit=None, oldest_first=True):
    #     if message.author.name != 'wd-tod':
    #         if 'o' in message.content and not any(char.isdigit() for char in message.content):
    #             messages.append((message.author.display_name, message.content))
    #             authors_without_number.add(message.author.display_name)

    # df = pd.DataFrame(messages, columns=['author', 'message'])

    # # Sort the DataFrame by 'author' and 'message'
    # df_sorted = df.sort_values(['author', 'message'])

    # print(df_sorted)
    # print("Authors without a number following 'o':")
    # for author in authors_without_number:
    #     print(author)