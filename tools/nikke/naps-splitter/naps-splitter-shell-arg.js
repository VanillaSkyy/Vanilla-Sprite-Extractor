"use strict";
/**
 * This program will empty the naps directory of the NAU files, be sure to clone it before launching it or you'll need to redownload a good chunk of the game if you point to the game's own naps
 *
 */
var __awaiter = (this && this.__awaiter) || function (thisArg, _arguments, P, generator) {
    function adopt(value) { return value instanceof P ? value : new P(function (resolve) { resolve(value); }); }
    return new (P || (P = Promise))(function (resolve, reject) {
        function fulfilled(value) { try { step(generator.next(value)); } catch (e) { reject(e); } }
        function rejected(value) { try { step(generator["throw"](value)); } catch (e) { reject(e); } }
        function step(result) { result.done ? resolve(result.value) : adopt(result.value).then(fulfilled, rejected); }
        step((generator = generator.apply(thisArg, _arguments || [])).next());
    });
};
var __asyncValues = (this && this.__asyncValues) || function (o) {
    if (!Symbol.asyncIterator) throw new TypeError("Symbol.asyncIterator is not defined.");
    var m = o[Symbol.asyncIterator], i;
    return m ? m.call(o) : (o = typeof __values === "function" ? __values(o) : o[Symbol.iterator](), i = {}, verb("next"), verb("throw"), verb("return"), i[Symbol.asyncIterator] = function () { return this; }, i);
    function verb(n) { i[n] = o[n] && function (v) { return new Promise(function (resolve, reject) { v = o[n](v), settle(resolve, reject, v.done, v.value); }); }; }
    function settle(resolve, reject, d, v) { Promise.resolve(v).then(function(v) { resolve({ value: v, done: d }); }, reject); }
};
var __importDefault = (this && this.__importDefault) || function (mod) {
    return (mod && mod.__esModule) ? mod : { "default": mod };
};
Object.defineProperty(exports, "__esModule", { value: true });
/**
 * everything related to a unity sub folder have been commented because it can just stay in the naps and saves a lot of time
 * saves ~ 20 000 file copies and deletion, which is 80% of the files > make the script 5 times faster
 * if needs be, uncomment the lines associated
 */
const node_fs_1 = __importDefault(require("node:fs"));
const naps_path = "./naps"; // cloned naps folder from Unity folder
const aeb_path = "./aeb"; // target folder for files that need NAU processing
const unity_path = "./unity"; // target folder for files that doesn't need NAU processing
let aeb_count = 0;
let unity_count = 0;
const unity_nkab_checker = (dir, file) => __awaiter(void 0, void 0, void 0, function* () {
    const path = dir + '/' + file;
    return new Promise((resolve) => __awaiter(void 0, void 0, void 0, function* () {
        const firstBytes = yield node_fs_1.default.createReadStream(path).flatMap(chunk => new Uint8Array(chunk)).take(4).toArray();
        const arrayBuffer = new Uint8Array(firstBytes).buffer;
        const buffer = Buffer.from(arrayBuffer);
        // read if the buffer key is NKAB or UnityFS
        // if the 4 first bytes aren't NKAB, then defaults to UnityFs, there cannot be a 3rd option
        const key = buffer.toString('utf8');
        if (key.toLowerCase() === 'nkab') {
            node_fs_1.default.cpSync(path, `${aeb_path}/${file}`);
            node_fs_1.default.rmSync(path);
            aeb_count++;
        }
        else {
            // fs.cpSync(path, `${unity_path}/${file}`)
            // fs.rmSync(path)
            unity_count++;
        }
        resolve(true);
    }));
});
const subfolder_parser = (dir) => __awaiter(void 0, void 0, void 0, function* () {
    return new Promise((resolve) => __awaiter(void 0, void 0, void 0, function* () {
        var _a, e_1, _b, _c;
        const path = `${dir.path}/${dir.name}`;
        const files = node_fs_1.default.readdirSync(path);
        console.log(`Parsing ${path} into aeb or naps : ${files.length} files.`);
        try {
            for (var _d = true, files_1 = __asyncValues(files), files_1_1; files_1_1 = yield files_1.next(), _a = files_1_1.done, !_a; _d = true) {
                _c = files_1_1.value;
                _d = false;
                const f = _c;
                yield unity_nkab_checker(path, f);
            }
        }
        catch (e_1_1) { e_1 = { error: e_1_1 }; }
        finally {
            try {
                if (!_d && !_a && (_b = files_1.return)) yield _b.call(files_1);
            }
            finally { if (e_1) throw e_1.error; }
        }
        resolve(true);
    }));
});
const main = () => __awaiter(void 0, void 0, void 0, function* () {
    var _a, e_2, _b, _c;
    const start = new Date();
    if (!node_fs_1.default.existsSync(naps_path)) {
        console.log('Naps directory not detected : canceling script');
        process.exit(400);
    }
    // get a Dirent[] to get isFile/isDirectory methodes
    // Dirent type comes from withFileTypes = true
    const directories = node_fs_1.default.readdirSync(naps_path, { withFileTypes: true }).filter((f) => {
        return f.isDirectory() && f.name.startsWith(arg);
    });
    console.log(`\nFound ${directories.length} sub directories of ${naps_path}\n`);
    try {
        for (var _d = true, directories_1 = __asyncValues(directories), directories_1_1; directories_1_1 = yield directories_1.next(), _a = directories_1_1.done, !_a; _d = true) {
            _c = directories_1_1.value;
            _d = false;
            const dir = _c;
            yield subfolder_parser(dir);
        }
    }
    catch (e_2_1) { e_2 = { error: e_2_1 }; }
    finally {
        try {
            if (!_d && !_a && (_b = directories_1.return)) yield _b.call(directories_1);
        }
        finally { if (e_2) throw e_2.error; }
    }
    console.log(`\nFinished parsing ${aeb_count + unity_count} files : ${aeb_count} to ${aeb_path}, ${unity_count} stayed in naps (non NAU files). `);
    console.log(`Parsing took ${new Date().getTime() - start.getTime()} ms.`);
});
const arg = process.argv[2];
main();
