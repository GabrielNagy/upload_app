type tablou=array [1..2,1..2]of int64;
var t:tablou;
    m:int64;
    f,g:text;
 
procedure exp (var t:tablou; m:int64);
  var a:tablou;
  begin
    if m=1 then begin
                   t[1,1]:=0; t[1,2]:=1; t[2,2]:=1; t[2,1]:=1;
                end
    else begin
          exp(t,m shr 1);
          a[1,1]:=t[1,1]; a[1,2]:=t[1,2];  a[2,1]:=t[1,2]; a[2,2]:=t[2,2];
          t[1,1]:=(a[1,1]*a[1,1]+a[1,2]*a[2,1]) mod 666013;
          t[1,2]:=(a[1,1]*a[1,2]+a[1,2]*a[2,2]) mod 666013;
          t[2,1]:=(a[2,1]*a[1,1]+a[2,2]*a[2,1]) mod 666013;
          t[2,2]:=(a[2,1]*a[1,2]+a[2,2]*a[2,2]) mod 666013;
          if m and 1 =1 then begin
                                     a[1,1]:=t[1,1]; a[1,2]:=t[1,2];  a[2,1]:=t[1,2]; a[2,2]:=t[2,2];
                                     t[1,1]:=a[1,2] mod 666013;
                                     t[1,2]:=(a[1,1]+a[1,2]) mod 666013;
                                     t[2,1]:=a[2,2] mod 666013;
                                     t[2,2]:=(a[2,1]+a[2,2]) mod 666013;
                              end;
         end;
  end;
 
begin
assign(f,'kfib.in');
assign(g,'kfib.out');
reset(f);
rewrite(g);
read(f,m);
exp(t,m-1);
write(g,t[2,2]);
close(f);
close(g);
end.
