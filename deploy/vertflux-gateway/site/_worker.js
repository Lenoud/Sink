export default {
  async fetch(request, env) {
    return env.SINK_APP.fetch(request);
  },
};
