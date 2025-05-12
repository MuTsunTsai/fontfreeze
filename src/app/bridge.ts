
import { store } from "./store";

const worker = new Worker(new URL("./worker.ts", import.meta.url), { name: "worker" });

export const initialized = new Promise<void>((resolve, reject) => {
	const handler = (e: MessageEvent) => {
		if(e.data == "initialized") {
			worker.removeEventListener("message", handler);
			resolve();
		} else if("error" in e.data) {
			reject(new Error(e.data.error));
		} else if("progress" in e.data && store.loading) {
			store.loading = `packages (${e.data.progress}%)`;
		}
	};
	worker.addEventListener("message", handler);
});

export function callWorker(command: string, data?: unknown) {
	return new Promise((resolve, reject) => {
		const channel = new MessageChannel();
		worker.postMessage([command, data], [channel.port2]);
		channel.port1.onmessage = e => {
			const { success, data } = e.data;
			if(success) resolve(data);
			else reject(new Error(data));
		};
	});
}
