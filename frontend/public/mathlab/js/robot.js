/* Robot helpers for single/dual agent simulation */
'use strict';

(function () {
  function createRobot(id, options) {
    const o = options || {};
    return {
      id: id,
      label: o.label || id,
      color: o.color || '#14b8a6',
      state: {
        x: o.x || 0,
        y: o.y || 0,
        angle: (o.angleDeg || 0) * Math.PI / 180,
        dist: 0,
        speed: o.speed || 10,
        wheelAngle: 0,
        startX: o.startX != null ? o.startX : (o.x || 0),
        startY: o.startY != null ? o.startY : (o.y || 0),
        elapsed: 0
      },
      trail: [],
      stats: { totalDist: 0, totalTime: 0, turns: [], waits: 0 }
    };
  }

  function makeRobotApi(sim, id) {
    return {
      forward: cm => sim.forward(cm, id),
      backward: cm => sim.forward(-(cm || 0), id),
      move2d: (angle, cm) => sim.movePolar(angle, cm, id),
      goto: (x, y) => sim.gotoCm(x, y, id),
      faceAngle: deg => sim.faceAngle(deg, id),
      turn: deg => sim.turn(deg, id),
      turnLeft: deg => sim.turn(-(deg || 0), id),
      turnRight: deg => sim.turn(deg, id),
      setSpeed: v => sim.setSpeed(v, id),
      wait: sec => sim.wait((sec || 0) * 1000, id),
      stop: () => {}
    };
  }

  window.createRobot = createRobot;
  window.makeRobotApi = makeRobotApi;
})();
