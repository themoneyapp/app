const path = require("path");
const BundleTracker = require("webpack-bundle-tracker");
const MiniCssExtractPlugin = require("mini-css-extract-plugin");
const CssMinimizerPlugin = require("css-minimizer-webpack-plugin");
// const { SourceMapDevToolPlugin } = require("webpack");

module.exports = {
  target: "web",
  context: path.join(__dirname, "../"),
  entry: {
    project: path.resolve(__dirname, "../src/themoneyapp/static/themoneyapp/js/project"),
    vendors: path.resolve(__dirname, "../src/themoneyapp/static/themoneyapp/js/vendors"),
  },
  output: {
    path: path.resolve(__dirname, "../src/themoneyapp/static/webpack_bundles/themoneyapp/"),
    publicPath: "/static/webpack_bundles/themoneyapp/",
    filename: "js/[name]-[fullhash].js",
    chunkFilename: "js/[name]-[hash].js",
  },
  plugins: [
    new BundleTracker({
      path: path.resolve(path.join(__dirname, "../")),
      filename: "webpack-stats.json",
    }),
    new MiniCssExtractPlugin({ filename: "css/[name].[contenthash].css" }),
  ],
  module: {
    rules: [
      // we pass the output from babel loader to react-hot loader
      {
        test: /\.js$/,
        loader: "babel-loader",
      },
      {
        test: /\.s?css$/i,
        use: [
          MiniCssExtractPlugin.loader,
          "css-loader",
          {
            loader: "postcss-loader",
            options: {
              postcssOptions: {
                config: path.resolve(__dirname, "../postcss.config.js"),
              },
              // postcssOptions: postcssOptions,
              // postcssOptions: {
              //   plugins: ["postcss-preset-env", "autoprefixer", "tailwindcss"],
              // },
            },
          },
          // "sass-loader",
        ],
      },
    ],
  },
  optimization: {
    minimizer: [new CssMinimizerPlugin()],
  },
  resolve: {
    modules: ["node_modules"],
    extensions: [".js", ".jsx"],
  },
};
