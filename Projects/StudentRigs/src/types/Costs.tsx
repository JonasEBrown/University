export interface Costs {
	assembly: {
		hours: {
			min: number;
			max: number;
		};
		costPerHour: number;
	};
	support: {
		costPerHour: number;
	};
}
