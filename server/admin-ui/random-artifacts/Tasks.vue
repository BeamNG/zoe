<template>
  <div>
    <v-expansion-panels v-model="tasksPanel">
      <v-expansion-panel v-for="(task, taskName) in tasks" :key="taskName">
        <v-expansion-panel-header>
          <v-row>
            <b>{{taskName}}</b>  ({{Object.keys(tasks[taskName]).length}} Builds)
          </v-row>
        </v-expansion-panel-header>
        <v-expansion-panel-content>
          <v-row>
            <v-col cols="12" md="12">
              
              <v-expansion-panels v-model="buildPanel">
                <v-expansion-panel v-for="build_id in sortKeys(tasks[taskName])">
                  <v-expansion-panel-header>
                    <v-row>
                      Build {{build_id}}
                    </v-row>
                  </v-expansion-panel-header>
                  <v-expansion-panel-content>
                    <v-row>
                      <v-col cols="12" md="12">

                        <TaskView 
                          :tasks = "tasks[taskName][build_id]" 
                          >
                        </TaskView>

                      </v-col>
                    </v-row>
                  </v-expansion-panel-content>
                </v-expansion-panel>
              </v-expansion-panels>

            </v-col>
          </v-row>
        </v-expansion-panel-content>
      </v-expansion-panel>
    </v-expansion-panels>

    <!--
      <pre style="max-height: 100px;">{{ JSON.stringify(tasks, null, 2) }}</pre>
    -->
  </div>
</template>

<script>
import TaskView from './TaskView'
export default {
  metaInfo: {
    title: 'Tasks'
  },
  components: {
    TaskView,
  },
  data() {
    return {
      tasks: {},
      tasksPanel: 0,
      buildPanel: 0,
      taskPanel: 0,
    }
  },
  methods: {
    sortKeys(array) {
      return Object.keys(array).reverse()
    },
    _filterIncomingEvents(events) {
      // tasks > builds > events
      console.info("Received events:" , events)
      for (let event of events) {
        if(event.client === undefined) {
          event.client = this.$zoe.executors.find(ex => ex.clientData.machine_uuid === event.machineUUID);
        }
        // check if the task is there and all
        if(typeof event.task_id !== 'string') continue;
        let taskPath = event.task_id.split('/').filter(function (el) { return el != ''; });
        let rootTaskId = taskPath[0]
        if(!(rootTaskId in this.tasks)) {
          this.$set(this.tasks, rootTaskId, {})
        }
        
        // now the same for the build
        if(event.build_id === undefined || event.build_id === null) continue;
        if(typeof event.build_id == 'int') event.build_id = event.build_id.toString()
        if(!(event.build_id in this.tasks[rootTaskId])) {
          this.$set(this.tasks[rootTaskId], event.build_id, {})
        }
        
        // now the same for the sub tasks
        let subTaskPath = taskPath.slice(1).join('/')
        if(subTaskPath === '') subTaskPath = '/'
        if(!(subTaskPath in this.tasks[rootTaskId][event.build_id])) {
          this.$set(this.tasks[rootTaskId][event.build_id], subTaskPath, { 'result': false, 'events': []})
        }
        if(event.type === 'task_begin') {
          // ok, this is getting more involved X|
          // remove the last element of the path so the event start is in the parent
          subTaskPath = taskPath.slice(1, -1).join('/')
          if(subTaskPath === '') subTaskPath = '/'
          if(!(subTaskPath in this.tasks[rootTaskId][event.build_id])) {
            this.$set(this.tasks[rootTaskId][event.build_id], subTaskPath, { 'result': false, 'events': []})
          }
          let childTask = this.tasks[rootTaskId][event.build_id][subTaskPath]
          if(!('children' in this.tasks[rootTaskId][event.build_id][subTaskPath])) {
            this.tasks[rootTaskId][event.build_id][subTaskPath]['children'] = []
          }
          this.tasks[rootTaskId][event.build_id][subTaskPath]['children'].push(childTask)
        } else if(event.type === 'task_end') {
          this.tasks[rootTaskId][event.build_id][subTaskPath]['result'] = event.result
          //continue
        }

        this.tasks[rootTaskId][event.build_id][subTaskPath]['events'].push(event)
      }
      
      // sort things ..
      for (let taskName of Object.keys(this.tasks)) {
        for (let buildId of Object.keys(this.tasks[taskName])) {
          this.tasks[taskName][buildId]['/'].tree = []
          for (let subTaskName of Object.keys(this.tasks[taskName][buildId])) {
            this.tasks[taskName][buildId]['/'].tree.push({
              'name': subTaskName,
              //'icon': '',
            })
            //console.log(">>>", subTaskName, this.tasks[taskName][buildId][subTaskName].events)
            let events = this.tasks[taskName][buildId][subTaskName].events
            this.tasks[taskName][buildId][subTaskName].events = events.sort((a, b) => {
              return a.id < b.id
            })
          }
        }
      }

      console.log(this.tasks)
    }
  },
  created() {
    this.$zoe.send({ type: "getEvents" });
    this.$zoe.listen(['events'], events => {
      this._filterIncomingEvents(events)
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
