import Modal from "bootstrap/js/dist/modal";

export const modal = (selector: string | Element): Modal => Modal.getOrCreateInstance(selector);

export function clone<T>(obj: T): T {
	return JSON.parse(JSON.stringify(obj));
}
