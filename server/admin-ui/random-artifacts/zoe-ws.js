/// $zoe (global)
// see data definitions in code below
// it also has some alias function

/// $bngws (global)
//
// $bngws.listen(type, callback, [query])
//   listen for data by "type" field match in a response
// where:
//   type     - case insensitive "type" field from incoming data
//              multiple types can be specified as array, e.g. ["clients", "fileHashes"]
//   callback - function with three argument for convenience: data, type and raw
//              raw is the original data packet, data - raw.data and type - raw.type
//   query    - optional data to send to a server
//              it will be automatically resent on reconnect
// notes:
//   multiple listeners for the same type can be defined
//   if a same callback function for the type was already registered, it will be replaced (it must be an instance of that function)
//
// $bngws.unlisten([type], [callback], [query])
//   removes listener
//   if no arguments provided, all listeners will be wiped
//   if more than one argument provided, it will have to match both
//
// await $bngws.request(query, [state])
//   makes an async request, waiting for an answer that will be returned in place (only data field)
// $bngws.request(query, callback)
// $bngws.request(query, state, callback)
//   makes a request, returning it to a callback
//   callback(data, type, raw, lag)
//     where "lag" is a delay with a server in ms (FIXME: throttle affects calculated lag)
// note:
//   request will not prevent listeners from firing, except special types "?" and "!"
//
// $bngws.send({ a: 123 })
//   only sends the data
//
// all functions can be called at any time, their queries will be queued for sending after successful connection
// all commands (send-s and queries) are queued to be sent in a throttled sequence
// listen(), request() and send() will attempt to immediately reconnect if disconnected

import Vue from "vue";
import ws from "./ws";

Vue.use({
  install: app => {
    //const wsaddress = "ws://your-zoe-instance/ws/";
    const wsaddress = `ws://127.0.0.1:8000/ws/`;

    // detect if we're running locally
    const dev = window.location.host.indexOf("127.0.0.1") > -1;

    const zoe = Vue.observable({
      // define data here first
      serverVersion: "",
      executors: [],
      subscriptions: [], // reactive-unsafe

      // helpers and aliases
      send: ws.send,
      request: ws.request,
      refresh() { // force-refresh executors
        ws.send({ type: "getClients" });
      },
      listen() {
        ws.listen.apply(ws, arguments)
      },
    });
    // expose zoe-related data globally as $zoe
    app.prototype.$zoe = zoe;

    ws.connect(wsaddress);

    if (dev) {
      // catch all
      ws.listen("*", (data, type) => {
        if (type !== "webpong")
          console.log(`Zoe gossips about ${type}:`, data)
      });

      // catch undefined
      ws.listen("?", (data, type) => console.log(`Received unknown type "${type}"`));
      ws.listen("!", (data, type, raw) => console.log("Received unknown data (no type specified):", raw));
    }

    // listen for info
    ws.listen("clientInfo", data => zoe.serverVersion = data.ZoeServerVersion);
    ws.listen("subscriptions", data => zoe.subscriptions = data || [], { type: "subscriptions" });

    //ws.listen("log", data => console.info("LOG RECEIVED< DO STH ABOUT IT:" , data));

    // register, but don't listen for real type - we only want to have this call every time on connect
    ws.listen("_dummy", null, { type: "register", clientType: "webChat" });

    // listen for and get executors list
    ws.listen("clients", data => {
      if (typeof data !== "object" && !Array.isArray(data))
        return;
      // remove
      let ids = data.map(node => node.clientid);
      for (let i = zoe.executors.length - 1; i > -1; i--)
        if (!ids.includes(zoe.executors[i].clientid))
          zoe.executors.splice(i, 1);
      // update or add
      ids = zoe.executors.map(node => node.clientid);
      for (let node of data) {
        let i = ids.indexOf(node.clientid);
        if (i > -1)
          Vue.set(zoe.executors, i, node);
        else
          zoe.executors.push(node);
      }
    }, { type: "getClients" });


    // ws lib controls and data
    const bngws = Vue.observable(ws.data);
    bngws.connect = () => ws.connect(wsaddress);
    bngws.reconnect = () => {
      if (!ws.data.connected) {
        if (dev)
          console.log("Forcing reconnect...");
        ws.connect(wsaddress);
      } else {
        if (dev)
          console.log("Disconnecting... And after a short delay we will connect again.");
        ws.disconnect(true);
      }
    };
    for (let key in ws)
      if (key !== "data" && !bngws.hasOwnProperty(key))
        bngws[key] = ws[key];
    // expose ws control globally as $bngws
    app.prototype.$bngws = bngws;
  }
});
