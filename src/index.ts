import express, { Request, Response, NextFunction } from 'express';
import dotenv from 'dotenv';
import cors from 'cors';
import { InfluxDB } from '@influxdata/influxdb-client';
import WebSocket, { WebSocketServer } from 'ws';
import http from 'http';

dotenv.config();

const app = express();
app.use(cors());
const port = process.env.PORT || 3001;

const token = process.env.INFLUXDB_TOKEN || '';
const url = process.env.INFLUXDB_URL || 'https://us-east-1-1.aws.cloud2.influxdata.com';
const org = process.env.INFLUXDB_ORG || '';
const bucket = process.env.INFLUXDB_BUCKET || 'sensor_data';

const client = new InfluxDB({ url, token });
const queryApi = client.getQueryApi(org);

async function getHistoricalData(range: string): Promise<{ time: string; random: number }[]> {
  const totalPoints = 10;
  const timeRange = range.startsWith('-') ? range : `-${range}`;
  const hours = parseInt(range.replace(/\D/g, ''), 10);
  const windowDuration = `${hours / totalPoints}m`;

  const fluxQuery = 
  `
    from(bucket: "${bucket}")
    |> range(start: ${timeRange})
    |> filter(fn: (r) => r._measurement == "wifi_status" and r._field == "random")
    |> aggregateWindow(every: ${windowDuration}, fn: mean, createEmpty: false)
    |> sort(columns: ["_time"], desc: false)
  `;

  const data: { time: string; random: number }[] = [];

  return new Promise((resolve, reject) => {
    queryApi.queryRows(fluxQuery, {
      next(row, tableMeta) {
        const tableObject = tableMeta.toObject(row);
        data.push({
          time: new Date(tableObject._time).toISOString(),
          random: tableObject._value !== undefined ? Number(tableObject._value) : 0
        });
      },
      error(error) {
        console.error(`Error executing Flux query: ${error.message}`);
        reject(error);
      },
      complete() {
        resolve(data);
      }
    });
  });
}

app.use(express.static('public'));

app.get('/historical-data/:range', async (req: Request, res: Response) => {
  try {
    const { range } = req.params;
    const historicalData = await getHistoricalData(range);
    res.json(historicalData);
  } catch (err: any) {
    res.status(500).json({ error: err.message });
  }
});

const server = http.createServer(app);

const wss = new WebSocketServer({ noServer: true });

wss.on('connection', (ws: WebSocket) => {
  console.log('New client connected for real-time data');

  ws.on('message', (message: string) => {
    try {
      const sensorData = JSON.parse(message);
      console.log(sensorData)
      wss.clients.forEach((client) => {
        if (client.readyState === WebSocket.OPEN) {
          client.send(JSON.stringify(sensorData));
        }
      });
    } catch (error) {
      console.error('Error parsing sensor data:', error);
    }
  });

  ws.on('close', () => {
    console.log('Client disconnected');
  });
});


server.on('upgrade', (request: Request, socket, head) => {
  wss.handleUpgrade(request, socket, head, (ws) => {
    wss.emit('connection', ws, request);
  });
});

server.listen(port, () => {
  console.log(`Server running on port ${port}`);
});