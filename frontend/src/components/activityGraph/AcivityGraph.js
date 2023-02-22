import React from 'react'
import { useState } from "react";
import { useEffect } from 'react';
import { useCallback } from 'react';
import { useContext } from 'react';
import { useRef } from 'react';
import ForceGraph2D from 'react-force-graph-2d';
import "./activityGraph.css"
import "bootstrap/dist/css/bootstrap.min.css";
import { useWindowSize } from '@react-hook/window-size';
import { AppContext } from '../../context/Context';

const AcivityGraph = React.memo(()  => {

    var newData = {nodes: [], links: []};
    var data = useContext(AppContext);
    var [currentNode, setNode] = data["currentNode"]
    var [gData, setData] = data["gData"]
    var [currentConfig,setCurrentConfig] = data["currentConfig"]
    var [configs,setConfigs] = data["configs"]

    const [cacheData, setCacheData] =  useState({});
    const [cacheConfigs, setCacheConfigs] =  useState({});
    const [directory, setDirectory] =  useState("");
    const [loaded, setLoaded] = useState(false)

    const graphRef = useRef();

    const tryLoadData = () => {
      try {
       return require("../../data/config.json");
      } catch (err) {
       return null;
      }
    };

    let ref = graphRef.current

    if (!loaded) {
      try {
        ref.d3Force('charge').strength(-150)
        //ref.d3Force('link').distance(400)
        ref.d3Force('link').strength(0.0001)
        ref.zoom(0.5)
        setLoaded(true)
      }
      catch(err) {
        // console.log(err)
      } 
    }
    

    useEffect(() => {
      
      const interval = setInterval(() => {

           
        
        var readData = tryLoadData()

        if (readData !== null){

          var dataConfigs = readData.configs;     

          if (dataConfigs !== cacheData || cacheConfigs !== currentConfig){


            setConfigs(dataConfigs)
          // use config to get directory
          var isFound = false;
          for(var currentConfigIndex = 0; currentConfigIndex < dataConfigs.length; currentConfigIndex ++){
            var dataConfig = dataConfigs[currentConfigIndex]
              if (dataConfig.config.device === currentConfig.device && dataConfig.config.mode ===  currentConfig.mode && dataConfig.config.appName === currentConfig.appName){
                isFound = true
                loadDataForGraph(dataConfig)
              }

            }
            setCacheData(dataConfigs);
            setCacheConfigs(currentConfig);
          }
        }
      }, 2000);
    
      return () => clearInterval(interval);
    }, [gData,directory,currentConfig,cacheConfigs,cacheData]);

    const loadDataForGraph = dataConfig => {
      var folderPath = dataConfig.config.appName + "/" + dataConfig.config.device + "/" + dataConfig.config.mode + "/" ;
      setDirectory(folderPath);

      var sources = []
      for (var i=0; i<dataConfig.config.edges.length; i++) {
        var link = dataConfig.config.edges[i]
        if (link.source && link.destination) {
          newData.links.push(
            {
              "target":link.destination,
              "source":link.source
            }
          )
        }
        else {
          sources.push(link.destination)
        }
      }
        
      // set data for node
        var currentID = 0;
        let x=-graphWidth/2, y=0
        let max = 20;
        let min = -20
        for (var i = 0; i < dataConfig.config.activities.length; i++){
          var activityName = dataConfig.config.activities[i];

          for (var j = 0; j < dataConfig.config.nodes.length; j++) {
            var nodeName = dataConfig.config.nodes[j];
            if (nodeName.includes(activityName)) {  
              x += Math.floor(Math.random() * (max - min + 1)) + min;
              y += Math.floor(Math.random() * (max - min + 1)) + min;
              var newNode = {
                id: nodeName,
                img: activityName + "/" + nodeName + ".jpg",
                activity: activityName,
                activityId: i,
                nodeName: nodeName,
                config: folderPath,
                source: sources.includes(nodeName),
                x: x,
                y: y
              };
              if (currentID === 0) {
                setNode(newNode);
              }
              
              newData.nodes.push(newNode);
              currentID ++;
            }
          }

          x += 700;
          if (x > graphWidth){
            x = -graphWidth/2;
            y += 700;
          }
        }
        setData(newData);
    }

    const [width, height] = useWindowSize();
    const graphHeight = height * 0.92;
    const graphWidth = width/1.7;

    function getUniqueColor(n) {
      const rgb = [0, 0, 0];
  
      for (let i = 0; i < 24; i++) {
          rgb[i%3] <<= 1;
          rgb[i%3] |= n & 0x01;
          n >>= 1;
      }
  
      return '#' + rgb.reduce((a, c) => (c > 0x0f ? c.toString(16) : '0' + c.toString(16)) + a, '');
  }

  return (
    <div >
<ForceGraph2D
      ref={graphRef}
      graphData={gData}
      maxZoom = {20}
      forceEngine="d3"
      
      nodeCanvasObject={(node, ctx, globalScale) => { 
        var img = new Image(); 
        try {
          img.src = require( `../../data/${directory}activity_screenshots/${node.img}`)
        } catch (error) {
          
        }

        if(node.activity === currentNode.activity) {
          ctx.beginPath();
          ctx.fillStyle = "#fffb03";
          ctx.fillRect(node.x - 34, node.y - 69, 79, 139);
          ctx.stroke();
        }
        else{
          ctx.beginPath();
          ctx.fillStyle = getUniqueColor(node.activityId);
          ctx.fillRect(node.x - 34, node.y - 69, 79, 139);
          ctx.stroke();
        }

        ctx.drawImage(img, node.x - 32, node.y - 67, 75, 135);

        if (node.source) {
          var entry_img = new Image();
          entry_img.src = require(`../../images/entry.png`)  
          ctx.drawImage(entry_img, node.x-40, node.y-65, 40, 35)
        }

        if (node.nodeName === currentNode.nodeName) {
          var eye_img = new Image();
          eye_img.src = require(`../../images/eye.png`);
          ctx.drawImage(eye_img, node.x-20, node.y-18, 50, 30);
        }

        ctx.font = "10px Arial"
        ctx.textAlign = "center";
        ctx.fillText(node.activity, node.x, node.y+80);
        }}
        
        d3AlphaMin={0.01}
        linkDirectionalArrowLength={20}
        linkDirectionalArrowRelPos={0.5}
        linkDirectionalArrowColor={() => "black"}
        linkCurvature={0.25} 
        linkWidth={5}
        height= {graphHeight}
        width= {graphWidth} 
        onNodeClick={ node => {setNode(node)}}
        onNodeDragEnd={node => {
          node.fx = node.x;
          node.fy = node.y;
          node.fz = node.z;
        }}
        nodePointerAreaPaint={(node, color, ctx) => {
          ctx.fillStyle = color;
          ctx.fillRect(node.x - 32, node.y - 67, 96, 135);
        }}
        />
    </div>

   
  )
});

export default AcivityGraph