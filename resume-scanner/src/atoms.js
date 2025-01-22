import {
    atom,
} from "recoil";
import { recoilPersist } from 'recoil-persist';

const { persistAtom } = recoilPersist();

export const modeAtom = atom({
    key: 'mode',
    default: {
        isUploadMode: false,
        isJobMode: false
    },
    effects_UNSTABLE: [persistAtom],
});