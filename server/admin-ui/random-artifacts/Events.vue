<template>
  <v-row>
    <v-simple-table dense>
      <template v-slot:default>
        <thead>
          <tr>
            <th class="text-left">Client</th>
            <th class="text-left">Time</th>
            <th class="text-left">Severity</th>
            <th class="text-left">Message</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="evt in events" :class="'LOG_' + evt.loglevel">
            <td>{{ evt.client.clientData.name }}</td>
            <td>{{ evt.created_at }}</td>
            <td>{{evt.loglevel}}</td>
            <td>
              <div v-if="evt.task">
                {{ evt.type }} | {{ evt.task.id }} | {{evt.task.procState}} | {{ evt.task.title }}
              </div>
              <div v-else>
                {{ evt.message || evt.m }}
              </div>
            </td>
            <!-- TODO FIXME -->
            <v-tooltip>
            <pre>{{ JSON.stringify(events, null, 2) }}</pre>
            </v-tooltip>
          </tr>
        </tbody>
      </template>
    </v-simple-table>
  </v-row>
</template>

<script>
export default {
  metaInfo: {
    // title will be injected into parent titleTemplate
    title: 'Events'
  },
  data() {
    return {
      events: [],
    }
  },
  methods: {
  },
  created() {
    this.$zoe.send({ type: "getEvents" });
    this.$zoe.listen(['events'], events => {
      console.info("Received events:" , events)
      for (let event of events) {
        if(event.client === undefined) {
          event.client = this.$zoe.executors.find(ex => ex.clientData.machine_uuid === event.machineUUID);
        }
        this.events.push(event)
      }
    });
    this.$zoe.send({ type: "subscribeEvents" });
  }
}
</script>
<style lang="scss" scoped>
.LOG_DEBUG { background-color: #b3ffde }
.LOG_INFO { background-color: #74ed94 }
.LOG_WARNING { background-color: #ffbd7a }
.LOG_ERROR { background-color: #ff7a7a }
.LOG_CRITICAL { background-color: #ff4747 }
</style>
