// shard.js
const { ClusterManager } = require("discord-hybrid-sharding");
require("dotenv").config();
process.env.DEBUG = "discord-hybrid-sharding:*";

const client = require("./bot.js");

const manager = new ClusterManager(`${__dirname}/bot.js`, {
  totalShards: 4,
  shardsPerCluster: 2,
  mode: "process",
  token: process.env.TOKEN,
});

process.on("unhandledRejection", (error) => {
  console.error("Unhandled promise rejection:", error);
});

manager.on("clusterCreate", (cluster) => {
  console.log(`Launched Cluster ${cluster.id}`);

cluster.on("ready", () => {
  console.log(`Cluster ${cluster.id} is now ready!`);
  });
});

manager.spawn();