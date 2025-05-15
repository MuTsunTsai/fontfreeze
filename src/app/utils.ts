import Modal from "bootstrap/js/dist/modal";

export const modal = (selector: string): Modal => Modal.getOrCreateInstance(selector);

export function clone<T>(obj: T): T {
	return JSON.parse(JSON.stringify(obj));
}
