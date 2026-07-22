const path = require("path");

module.exports = {
  entry: {
    taskpane: "./src/taskpane.ts",
    index: "./src/index.ts"
  },
  devServer: {
    port: 3000,
    https: true,
    static: [
      {
        directory: path.join(__dirname, "src"),
      },
      {
        directory: path.join(__dirname, "dist"),
      }
    ]
  },
  module: {
    rules: [
      {
        test: /\.ts$/,
        use: "ts-loader",
        exclude: /node_modules/
      }
    ]
  },
  resolve: {
    extensions: [".ts", ".js"]
  },
  output: {
    filename: "[name].js",
    path: path.resolve(__dirname, "dist")
  }
};
