// bot.js
const { Client, IntentsBitField } = require("discord.js");
const openai = require("openai");
require("dotenv").config();

// Log the entire openai object to inspect its contents
console.log("OpenAI module:", openai);

const { Configuration, OpenAIApi } = openai;

// Log to verify the openai import
console.log("OpenAI Configuration:", Configuration);
console.log("OpenAI API:", OpenAIApi);

const client = new Client({
  intents: [
    IntentsBitField.Flags.Guilds,
    IntentsBitField.Flags.GuildMessages,
    IntentsBitField.Flags.MessageContent,
    IntentsBitField.Flags.GuildMessageReactions,
  ],
});

client.on("messageCreate", async (message) => {
  if (message.author.bot) return;
  if (message.channel.id !== process.env.CHANNEL_ID) return; 
  if (message.content.startsWith("$")) return;
  try {
    if (message.content === "*Ping") {
      message.reply(`${client.ws.ping} Pong!`);
      return;
    }
    
  } catch (error) {
    console.error("Error in messageCreate event:", error);
  }
});

const configuration = new Configuration({
  apiKey: process.env.API_KEY,
});

console.log("Configuration created successfully");

const openaiApi = new OpenAIApi(configuration);
console.log("OpenAIApi instance created successfully");

client.on("ready", async () => {
  try {
    console.log(`Bot has been successfully established on Shard ${client.shard.ids}`);
    const chat = client.channels.cache.get("1069983788236550154");
    if (chat) {
      chat.send(`Bot has been successfully launched on Shard ${client.shard.ids}`);
    }
  } catch (error) {
    console.error("Error in ready event:", error);
  }
});

client.on("messageCreate", async (message) => {
  if (message.author.bot) return;

  let conversationLog = [{
    role: "system",
    content: "You are a friendly chatbot."
  }];

  await message.channel.sendTyping();

  let prevMessages = await message.channel.messages.fetch( { limit:20 } );
  prevMessages.reverse();
  prevMessages.forEach((msg) => {
    if (message.content.startsWith("$")) return;
    if (msg.author.id !== client.user.id && message.author.bot) return;
    if (msg.author.id !== message.author.id) return;

    conversationLog.push({
      role: "user",
      content: msg.content,
    });
  });

  try {
    const result = await openaiApi.createChatCompletion({
      model: "gpt-3.5-turbo",
      messages: conversationLog,
    });

    message.reply(result.data.choices[0].message);
  } catch (error) {
    console.error("Error in OpenAI API request:", error);
    message.reply("Sorry, there was an error processing your request.");
  }
});

client.login(process.env.TOKEN);

module.exports = client;
